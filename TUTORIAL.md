# How to run a data collection
Once the application is open, you'll see the following screen:

![image](https://github.com/user-attachments/assets/a2b9454e-471a-4da4-82c1-1ff39e42efda)

Refer to this [guide](README.md) to troubleshoot the application opening.

Click on the "Configure new capture" button to be redirected to the capture configuration screen:

![image](https://github.com/user-attachments/assets/c363f1af-510e-4bef-a965-abea6431a611)

In this step, you'll configure:

- Select among the detected devices one camera to be used for capturing
- Select a folder to create your PERCLOS reports
- Provide an arbitrary participant ID for the capture
- Selected advanced perclos configuration (Optional)

If you click the "Advanced Configurations" button, you'll be able to change PERCLOS capture parameters:

![image](https://github.com/user-attachments/assets/cf566b3d-ce3f-440b-adb4-c6c8ae5b4951)


Once the capture is fully configured, click save and start to be redirectioned to the Capture Feed:

![image](https://github.com/user-attachments/assets/6deb4034-9fd7-4b42-92a6-528c0a9b0d14)


In this screen, you'll see a live view of your camera but _**no data is being captured yet.**_ 

To start the capture, insert one condition (differentiate multiple captures for the same participant id) and hit "Start Trial".

 ![image](https://github.com/user-attachments/assets/f4c6713d-6c0a-4ce2-92b5-289b04f13478)


Finish the capture by clicking "Exit" or "End Trial". Refer to the next section to find your results

**Warning: if you end the trial in a different way (i.e closing the application) your results will not be produced.**

# Visualizing the results
The capture results will be available in the folder specified as report location selected in the capture configuration. 
Palpebra will create a folder named with the participant id, the condition and the start time timestamp, containing three files:

- config.csv: CSV file contatining the configurations used in the capture
- data.csv: CSV file containing the raw data 
- final_report.xlsx: Excel spreadsheet containing the raw data and one workbook with a summary (average eye opening, average perclos and capture duration)

The diagnosis folder contains debug data that don't comprehend PERCLOS analysis.

![image](https://github.com/user-attachments/assets/346ac011-81bb-4406-948b-1d6bd9b817fa)


