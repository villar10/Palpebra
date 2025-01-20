from pygrabber.dshow_graph import FilterGraph

def find_cameras() -> dict:
    devices = FilterGraph().get_input_devices()

    available_cameras = {}

    for device_index, device_name in enumerate(devices):
        available_cameras[device_index] = device_name

    return available_cameras