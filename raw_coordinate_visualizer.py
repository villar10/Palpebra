import argparse
import ast
import json
import math
from typing import Any, List, Optional, Sequence, Tuple

import cv2
import numpy as np
import pandas as pd


DEFAULT_TS_FORMAT = "%Y-%m-%d-%H-%M-%S-%f"  # e.g., 2025-09-04-16-39-28-685863


def find_timestamp_column(cols: Sequence[str]) -> str:
    """Pick a timestamp-like column name, fallback to the first column."""
    lower = [c.lower() for c in cols]
    for cand in ("timestamp", "time", "ts", "frame_time", "t"):
        if cand in lower:
            return cols[lower.index(cand)]
    return cols[0]


def _looks_number(x: Any) -> bool:
    try:
        float(x)
        return True
    except Exception:
        return False


def coerce_points(obj: Any) -> Optional[List[Tuple[float, float, float]]]:
    """
    Turn a cell into a list of (x,y,z) tuples.
    Accepts:
      - NaN / None  -> None
      - string repr of list-of-lists, e.g. '[[x,y,z], [x,y,z]]'
      - string repr of single triple, e.g. '[x,y,z]'
      - comma 'x,y,z'
      - already-a-list/tuple forms
    """
    if obj is None or (isinstance(obj, float) and math.isnan(obj)):
        return None

    val = obj
    if isinstance(obj, str):
        s = obj.strip()
        if not s:
            return None
        # Try JSON first
        try:
            val = json.loads(s)
        except Exception:
            # Make literal_eval friendly if there are "nan"/"NaN"/"NONE"
            s2 = s.replace("nan", "None").replace("NaN", "None").replace("NONE", "None")
            try:
                val = ast.literal_eval(s2)
            except Exception:
                parts = [p.strip() for p in s.split(",")]
                if len(parts) == 3:
                    try:
                        x, y, z = map(float, parts)
                        return [(x, y, z)]
                    except Exception:
                        return None
                return None

    if isinstance(val, (list, tuple)):
        if len(val) == 0:
            return None
        if len(val) == 3 and all(isinstance(v, (int, float)) or _looks_number(v) for v in val):
            try:
                x, y, z = map(float, val)
                return [(x, y, z)]
            except Exception:
                return None
        pts: List[Tuple[float, float, float]] = []
        for item in val:
            if isinstance(item, (list, tuple)) and len(item) >= 2:
                try:
                    x = float(item[0])
                    y = float(item[1])
                    z = float(item[2]) if len(item) > 2 else 0.0
                    if not (math.isfinite(x) and math.isfinite(y) and math.isfinite(z)):
                        continue
                    pts.append((x, y, z))
                except Exception:
                    continue
        return pts if pts else None

    return None


def compute_frames_per_row(
    timestamps: pd.Series, target_fps: float, ts_format: Optional[str]
) -> List[int]:
    """
    For each row i, compute how many frames to emit to approximate the elapsed time
    until the next row, at a constant video FPS. The last row uses the median positive delta.
    """
    dt = None
    if ts_format:
        # strip whitespace to avoid surprises
        ts_clean = timestamps.astype(str).str.strip()
        dt = pd.to_datetime(ts_clean, format=ts_format, errors="coerce")
    else:
        dt = pd.to_datetime(timestamps, errors="coerce")

    if not dt.isna().all():
        # seconds between rows via vectorized datetime ops
        deltas = dt.diff().dt.total_seconds().fillna(0).to_numpy()
    else:
        # treat as numeric seconds if possible
        s = pd.to_numeric(timestamps, errors="coerce")
        s = s.replace([np.inf, -np.inf], np.nan)
        if s.isna().all():
            return [1] * len(timestamps)
        deltas = s.diff().fillna(0).to_numpy()

    positive = [d for d in deltas if d > 0]
    median_dt = float(np.median(positive)) if positive else (1.0 / max(target_fps, 1e-9))

    frames_each: List[int] = []
    for d in deltas:
        d_sec = d if d > 0 else median_dt
        n = max(1, int(round(d_sec * target_fps)))
        frames_each.append(n)
    return frames_each


def open_video_writer(out_path: str, fps: float, size: Tuple[int, int]) -> cv2.VideoWriter:
    """Try a few codecs; return an opened VideoWriter or a dummy that isOpened()==False."""
    W, H = size
    tried = []

    def _try(fourcc_str: str):
        fourcc = cv2.VideoWriter_fourcc(*fourcc_str)
        vw = cv2.VideoWriter(out_path, fourcc, fps, (W, H))
        tried.append(fourcc_str)
        return vw

    # Prefer MP4 codecs when extension is .mp4
    if out_path.lower().endswith(".mp4"):
        for cc in ("mp4v", "avc1", "H264", "X264"):
            vw = _try(cc)
            if vw.isOpened():
                return vw

    # AVI fallbacks (robust on Windows)
    if out_path.lower().endswith(".avi"):
        for cc in ("MJPG", "XVID"):
            vw = _try(cc)
            if vw.isOpened():
                return vw

    # Try MP4 then AVI as generic fallbacks
    for cc in ("mp4v", "MJPG"):
        vw = _try(cc)
        if vw.isOpened():
            return vw

    return _try("xxxx")  # unopened sentinel


def main():
    ap = argparse.ArgumentParser(description="Visualize eye landmark columns to video.")
    ap.add_argument("--csv", required=True, help="Path to the CSV file (e.g., data.csv)")
    ap.add_argument("--out", required=True, help="Output video path (e.g., output.mp4 or output.avi)")
    ap.add_argument("--width", type=int, default=680, help="Frame width in pixels")
    ap.add_argument("--height", type=int, default=480, help="Frame height in pixels")
    ap.add_argument("--fps", type=float, default=30.0, help="Target video FPS (constant)")
    ap.add_argument("--radius", type=int, default=3, help="Base dot radius in pixels")
    ap.add_argument("--use_z_size", action="store_true",
                    help="If set, scale dot radius by z (relative to face width).")
    ap.add_argument("--z_alpha", type=float, default=0.25,
                    help="Sensitivity of z-to-size mapping (radius *= 1 + z * z_alpha).")
    ap.add_argument("--bg", choices=["black", "white"], default="black", help="Background color")
    ap.add_argument("--timestamp_format", default=DEFAULT_TS_FORMAT,
                    help="pandas/strftime format for timestamps; default matches 'YYYY-MM-DD-HH-MM-SS-ffffff'")
    args = ap.parse_args()

    W, H = args.width, args.height

    df = pd.read_csv(args.csv)
    if df.shape[1] < 7:
        raise ValueError("Expected at least 7 columns (timestamp + 6 marker columns). Found: %d" % df.shape[1])

    # Timestamp + last 6 marker columns
    ts_col = find_timestamp_column(df.columns)
    marker_cols = list(df.columns[-6:])

    # Timing (strict parse, no deprecated args)
    frames_per_row = compute_frames_per_row(df[ts_col], args.fps, args.timestamp_format)

    # Colors (BGR for OpenCV): red, green, blue, cyan, magenta, yellow
    palette = [
        (0, 0, 255),
        (0, 255, 0),
        (255, 0, 0),
        (255, 255, 0),
        (255, 0, 255),
        (0, 255, 255),
    ]

    # Video writer with fallbacks
    vw = open_video_writer(args.out, args.fps, (W, H))
    if not vw.isOpened():
        raise RuntimeError(
            "Could not open VideoWriter for '%s'. "
            "Try using a different extension (e.g., .avi) or a different path/codec." % args.out
        )

    bg_color = (0, 0, 0) if args.bg == "black" else (255, 255, 255)
    text_color = (255, 255, 255) if args.bg == "black" else (0, 0, 0)

    # Text overlay
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 0.5
    thickness = 1
    ts_origin = (10, H - 10)

    # Relative time for overlay: strict format
    ts_clean = df[ts_col].astype(str).str.strip()
    dt = pd.to_datetime(ts_clean, format=args.timestamp_format, errors="coerce")
    if dt.isna().all():
        rel_t = pd.to_numeric(df[ts_col], errors="coerce").replace([np.inf, -np.inf], np.nan)
        rel_t = None if rel_t.isna().all() else (rel_t - float(rel_t.iloc[0]))
    else:
        rel_t = (dt - dt.iloc[0]).dt.total_seconds()

    for i, row in df.iterrows():
        frame = np.full((H, W, 3), bg_color, dtype=np.uint8)

        # Draw per-column landmarks
        for j, col in enumerate(marker_cols):
            color = palette[j % len(palette)]
            pts = coerce_points(row[col])
            if pts is None:
                continue  # draw nothing for missing data

            for (x, y, z) in pts:
                if not (math.isfinite(x) and math.isfinite(y)):
                    continue
                xi = int(round(x))
                yi = int(round(y))
                if xi < 0 or yi < 0 or xi >= W or yi >= H:
                    continue

                r = int(args.radius)
                if args.use_z_size and math.isfinite(z):
                    r = max(1, min(12, int(round(args.radius * (1.0 + z * args.z_alpha)))))

                cv2.circle(frame, (xi, yi), r, color, thickness=-1, lineType=cv2.LINE_AA)

        # Timestamp overlay
        ts_raw = str(row[ts_col])
        if rel_t is not None and pd.notna(rel_t.iloc[i]):
            overlay = f"{ts_raw}   (t={float(rel_t.iloc[i]):.3f}s)"
        else:
            overlay = ts_raw
        cv2.putText(frame, overlay, ts_origin, font, font_scale, text_color, thickness, cv2.LINE_AA)

        # Emit frames to approximate elapsed time until next row
        n_emit = frames_per_row[i] if i < len(frames_per_row) else 1
        for _ in range(max(1, n_emit)):
            vw.write(frame)

    vw.release()
    print(f"Wrote video to: {args.out}")


if __name__ == "__main__":
    main()
