# Palpebra: Perclos Data Collection GUI
This project is an open-source option for performing perclos data collection using a webcam. Check our [guide](TUTORIAL.md) for data collection
## Dev dependencies
Make sure to initialize a virtual environment. At this time, only Python version 3.12.1 is supported.
All the dependencies are listed in the requirements.txt file. To install them using pip, you may run the following command from the root directory:

```
pip install -r requirements.txt
```

In order to run the program correctly, go to /(virtual-environment-path)/Lib/site-packages find the directory FaceAnalyzer, open the FaceAnalyzer.py file and remove all unused imports, since some of them are breaking due to deprecations.
All numpy data types (e.g., np.int()) will need to be changed to Python native data types for np deprecation of these data types.
Also, change line 1034 to the following:

```python
perclos = ((pb<threshold).astype(int).sum())/len(buffer)
```

These changes are needed only the first time you run the project in a dev environment.

## Running from source code
To run the application, simply run the main.py program by executing

```bash
python main.py
```

Note that if the tool is not able to detect or access your camera, it may be due to background applications holding a lock on the device. Zoom and Microsoft Teams are potential background applications that hold these devices. Please close these applications and try again.

## Packaging
The application installer was built using PyInstaller and InstallForge. Those tools generated a Windows-based .exe file, as specified in the book
Packaging Python Applications (Martin Fitzpatrick)
The library used for face detection has hard-coded file references which breaks PyInstaller builds. In order to build the application correctly, run:

```
pyinstaller -n "palpebra" --windowed main.py
```

This command will generate a .spec file as wells as the build and dist directories.
Then, change the Analysis constructor call in the .spec file, passing the datas parameter as the following:

```
datas=[(<path>\\env\\Lib\\site-packages\\mediapipe\\modules\\face_landmark\\face_landmark_front_cpu.binarypb', 'mediapipe/modules/face_landmark/'),('<path>\\env\\Lib\\site-packages\\mediapipe\\modules\\face_landmark\\face_landmark_with_attention.tflite', 'mediapipe/modules/face_landmark/'),('<path>\\env\\Lib\\site-packages\\mediapipe\\modules\\face_detection\\face_detection_short_range.tflite', 'mediapipe/modules/face_detection/')]
```

Change the path placeholder to the root location of the project

And run

```
pyinstaller palpebra.spec
```

After that, the dist folder contains the packaged application, that can be further used by InstallForge to build the executable. 
