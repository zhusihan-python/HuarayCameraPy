1. Python samples rely on SDK Ver2.1.0_Build20180129.
   Please install correct SDK version before run samples.

2. Python APIs in SDK are actually converted from APIs in C language to ctypes interface which can be used by python directly. (please refer to include content for head files)
   Relationships between C and python are shown as following:
    · SDK.h -> MVSDK.py
    · ImageConvert.h -> ImageConvert.py   ※Image format transcoding module
	· RecordVideo.h -> RecordVideo.py	  ※Record video module
	
3. The samples are compatible with python2 and python3.
   Before run a sample, please install python and set system environment variables corresponding with python correctly.
   
   And then enter "python ./Demo.py" to run the sample.

4. Sample is 64bit by default.
   If 32bit sample is necessary, please correct process of loading library of SDK, as shown below:
   · MVSDK.py        ： comment Line20, uncomment Line18
   · ImageConvert.py ： comment Line15，uncomment Line13
   · RecordVideo.py  ： comment Line15，uncomment Line13

5. Python samples show following functions:
   · Discover camera;
   · Connect/Disconnect camera;
   · Start getting frames/Stop getting frames;
   · Set software/external trigger mode;
   · Get single frame (under software trigger mode);
   · Save .Bmp picture;
   · Volunteer to get frame or callback to get frame;
   · Set ROI and exposure time;
   · Record video--RecordVideo.py

6. About settings of reading and writing parameters, SDK provides two methods:

6.1.SDK provides parameter nodes to access the parameters:
Create a control node according to the object, and then create a parameter node according to control node, so a parameter can be read and written;
In samples, setting software/external trigger（setSoftTriggerConf/setLineTriggerConf） modes are realized by this method.


6.2.Common parameters configuration(node)
According to the types of parameters (such as double, int, bool and ect., view it in the client), create a node with name of parameter, so a parameter can be read and written. In samples, setting exposure time and ROI (setExposureTime/setROI) are realized by this method.	  

7. Note

7.1.Python can only run sample with correct bits, i.e.32bit python can only support 32 bit python samples, 64 bit python can only support 64bit python samples.
   
7.2.While using APIs in C language please notice node type and that release internal resources of node by calling release APIs.
    Samples show usage and explanation.


- END -
