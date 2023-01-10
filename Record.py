#!/usr/bin/env python
# coding: utf-8
'''
Created on 2022-05-23

@author: 
'''

from MVSDK import *
from RecordVideo import *
import sys
import threading

g_cameraStatusUserInfo = b"statusInfo"

# 相机连接状态回调函数
# camera connection status change callback
def deviceLinkNotify(connectArg, linkInfo):
    if ( EVType.offLine == connectArg.contents.m_event ):
        print("camera has off line, userInfo [%s]" %(c_char_p(linkInfo).value))
    elif ( EVType.onLine == connectArg.contents.m_event ):
        print("camera has on line, userInfo [%s]" %(c_char_p(linkInfo).value))

connectCallBackFuncEx = connectCallBackEx(deviceLinkNotify)

# 注册相机连接状态回调
# subscribe camera connection status change
def subscribeCameraStatus(camera):
    # 注册上下线通知
    # subscribe connection status notify
    eventSubscribe = pointer(GENICAM_EventSubscribe())
    eventSubscribeInfo = GENICAM_EventSubscribeInfo()
    eventSubscribeInfo.pCamera = pointer(camera)
    nRet = GENICAM_createEventSubscribe(byref(eventSubscribeInfo), byref(eventSubscribe))
    if ( nRet != 0):
        print("create eventSubscribe fail!")
        return -1

    nRet = eventSubscribe.contents.subscribeConnectArgsEx(eventSubscribe, connectCallBackFuncEx, g_cameraStatusUserInfo)
    if ( nRet != 0 ):
        print("subscribeConnectArgsEx fail!")
        # 释放相关资源
        # release subscribe resource before return
        eventSubscribe.contents.release(eventSubscribe)
        return -1

    # 不再使用时，需释放相关资源
    # release subscribe resource at the end of use
    eventSubscribe.contents.release(eventSubscribe)
    return 0

# 反注册相机连接状态回调
# unsubscribe camera connection status change
def unsubscribeCameraStatus(camera):
    # 反注册上下线通知
    # unsubscribe connection status notify
    eventSubscribe = pointer(GENICAM_EventSubscribe())
    eventSubscribeInfo = GENICAM_EventSubscribeInfo()
    eventSubscribeInfo.pCamera = pointer(camera)
    nRet = GENICAM_createEventSubscribe(byref(eventSubscribeInfo), byref(eventSubscribe))
    if ( nRet != 0):
        print("create eventSubscribe fail!")
        return -1

    nRet = eventSubscribe.contents.unsubscribeConnectArgsEx(eventSubscribe, connectCallBackFuncEx, g_cameraStatusUserInfo)
    if ( nRet != 0 ):
        print("unsubscribeConnectArgsEx fail!")
        # 释放相关资源
        # release subscribe resource before return
        eventSubscribe.contents.release(eventSubscribe)
        return -1

    # 不再使用时，需释放相关资源
    # release subscribe resource at the end of use
    eventSubscribe.contents.release(eventSubscribe)
    return 0

# 打开相机
# open camera
def openCamera(camera):
    # 连接相机
    # connect camera
    nRet = camera.connect(camera, c_int(GENICAM_ECameraAccessPermission.accessPermissionControl))
    if ( nRet != 0 ):
        print("camera connect fail!")
        return -1
    else:
        print("camera connect success.")
  
    # 注册相机连接状态回调
    # subscribe camera connection status change
    nRet = subscribeCameraStatus(camera)
    if ( nRet != 0 ):
        print("subscribeCameraStatus fail!")
        return -1

    return 0

# 关闭相机
# close camera
def closeCamera(camera):
    # 反注册相机连接状态回调
    # unsubscribe camera connection status change
    nRet = unsubscribeCameraStatus(camera)
    if ( nRet != 0 ):
        print("unsubscribeCameraStatus fail!")
        return -1
  
    # 断开相机
    # disconnect camera
    nRet = camera.disConnect(byref(camera))
    if ( nRet != 0 ):
        print("disConnect camera fail!")
        return -1
    
    return 0

# 枚举相机
# enumerate camera
def enumCameras():
    # 获取系统单例
    # get system instance
    system = pointer(GENICAM_System())
    nRet = GENICAM_getSystemInstance(byref(system))
    if ( nRet != 0 ):
        print("getSystemInstance fail!")
        return None, None

    # 发现相机
    # discover camera 
    cameraList = pointer(GENICAM_Camera()) 
    cameraCnt = c_uint()
    nRet = system.contents.discovery(system, byref(cameraList), byref(cameraCnt), c_int(GENICAM_EProtocolType.typeAll));
    if ( nRet != 0 ):
        print("discovery fail!")
        return None, None
    elif cameraCnt.value < 1:
        print("discovery no camera!")
        return None, None
    else:
        print("cameraCnt: " + str(cameraCnt.value))
        return cameraCnt.value, cameraList

def record():
    # 发现相机
    # enumerate camera
    cameraCnt, cameraList = enumCameras()
    if cameraCnt is None:
        return -1

    # 显示相机信息
    # print camera info
    for index in range(0, cameraCnt):
        camera = cameraList[index]
        print("\nCamera Id = " + str(index))
        print("Key           = " + str(camera.getKey(camera)))
        print("vendor name   = " + str(camera.getVendorName(camera)))
        print("Model  name   = " + str(camera.getModelName(camera)))
        print("Serial number = " + str(camera.getSerialNumber(camera)))

    camera = cameraList[0]

    # 打开相机
    # open camera
    nRet = openCamera(camera)
    if (nRet != 0):
        print("openCamera fail.")
        return -1

    # 创建流对象
    # create stream source object
    streamSourceInfo = GENICAM_StreamSourceInfo()
    streamSourceInfo.channelId = 0
    streamSourceInfo.pCamera = pointer(camera)
    streamSource = pointer(GENICAM_StreamSource())
    nRet = GENICAM_createStreamSource(pointer(streamSourceInfo), byref(streamSource))
    if ( nRet != 0 ):
        print("create StreamSource fail!")
        return -1

    # 通用属性设置:设置触发模式为off --根据属性类型，直接构造属性节点。如触发模式是 enumNode，构造enumNode节点
    # create corresponding property node according to the value type of property, here is enumNode
    # 自由拉流：TriggerMode 需为 off
    # set trigger mode to Off for continuously grabbing
    trigModeEnumNode = pointer(GENICAM_EnumNode())
    trigModeEnumNodeInfo = GENICAM_EnumNodeInfo()
    trigModeEnumNodeInfo.pCamera = pointer(camera)
    trigModeEnumNodeInfo.attrName = b"TriggerMode"
    nRet = GENICAM_createEnumNode(byref(trigModeEnumNodeInfo), byref(trigModeEnumNode))
    if (nRet != 0):
        print("create TriggerMode Node fail!")
        # 释放相关资源
        # release node resource before return
        sys.exit()

    nRet = trigModeEnumNode.contents.setValueBySymbol(trigModeEnumNode, b"Off")
    if (nRet != 0):
        print("set TriggerMode value [Off] fail!")
        # 释放相关资源
        # release node resource before return
        trigModeEnumNode.contents.release(trigModeEnumNode)
        sys.exit()

    # 需要释放Node资源
    # release node resource at the end of use
    trigModeEnumNode.contents.release(trigModeEnumNode)

    # 获取宽度
    # get the width of image
    widthNode = pointer(GENICAM_IntNode())
    widthNodeInfo = GENICAM_IntNodeInfo()
    widthNodeInfo.pCamera = pointer(camera)
    widthNodeInfo.attrName = b"Width"
    nRet = GENICAM_createIntNode(byref(widthNodeInfo), byref(widthNode))
    if (nRet != 0):
        print("create Width Node fail!")
        return -1

    nWidth = c_longlong()
    nRet = widthNode.contents.getValue(widthNode, byref(nWidth))
    if (nRet != 0):
        print("WidthNode getValue fail!")
        # 释放相关资源
        # release node resource before return
        widthNode.contents.release(widthNode)
        return -1
    # 释放相关资源
    # release node resource at the end of use
    widthNode.contents.release(widthNode)

    # 获取高度
    # get the height of image
    heightNode = pointer(GENICAM_IntNode())
    heightNodeInfo = GENICAM_IntNodeInfo()
    heightNodeInfo.pCamera = pointer(camera)
    heightNodeInfo.attrName = b"Height"
    nRet = GENICAM_createIntNode(byref(heightNodeInfo), byref(heightNode))
    if (nRet != 0):
        print("create Height Node fail!")
        return -1

    nHeight = c_longlong()
    nRet = heightNode.contents.getValue(heightNode, byref(nHeight))
    if (nRet != 0):
        print("HeightNode getValue fail!")
        # 释放相关资源
        # release node resource before return
        heightNode.contents.release(heightNode)
        return -1

    # 释放相关资源
    # release node resource at the end of use
    heightNode.contents.release(heightNode)

    stRecordPar = RECORD_SRecordParam()
    memset(byref(stRecordPar), 0, sizeof(RECORD_SRecordParam))

    stRecordPar.width = nWidth.value
    stRecordPar.height = nHeight.value
    # 视频帧率
    # video framerate
    stRecordPar.frameRate = 20
    # 视频质量（1~100）
    # video quality
    stRecordPar.quality = 30
    # 视频格式
    # video format
    stRecordPar.recordFmtType = RECORD_EVideoFormatType.RECORD_VIDEO_FMT_AVI
    # 保存路径
    # save path
    stRecordPar.recordFilePath = b"Record.avi"
    # 录像句柄
    # record handle
    handle = c_void_p()

    # 打开录像
    # open record
    nRet = openRecord(byref(stRecordPar), byref(handle))
    if 0 != nRet:
        print("打开录像失败，错误码：[%d]" % nRet)
        return -1

    # 开始拉流
    # start grabbing
    nRet = streamSource.contents.startGrabbing(streamSource, c_ulonglong(0), GENICAM_EGrabStrategy.grabStrartegySequential)
    if nRet != 0:
        print("自由拉流失败")
        return -1

    try:
        hThreadHandle = threading.Thread(target=work_thread, args=(streamSource,handle))
        hThreadHandle.start()
    except:
        print("error: unable to start thread")

    hThreadHandle.join()
    # 关闭录像
    # close record
    RecordVideodll.closeRecord(handle)

    # 停止拉流
    # stop grabbing
    nRet = streamSource.contents.stopGrabbing(streamSource)
    if (nRet != 0):
        print("stopGrabbing fail!")
        # 释放相关资源
        # release stream source object before return
        streamSource.contents.release(streamSource)
        return -1

    # 关闭相机
    # close camera
    nRet = closeCamera(camera)
    if (nRet != 0):
        print("closeCamera fail")
        # 释放相关资源
        # release stream source object before return
        streamSource.contents.release(streamSource)
        return -1

    # 释放相关资源
    # release stream source object at the end of use
    streamSource.contents.release(streamSource)
    return 0

def work_thread(streamSource,handle):
    imageCount=0
    frame = pointer(GENICAM_Frame())
    # 录制一帧图像所需要的参数
    stRecordFrameInfoParam = RECORD_SFrameInfo()

    # 主动取图
    # get one frame
    while imageCount < 200:
        nRet = streamSource.contents.getFrame(streamSource, byref(frame), c_uint(500))
        if (nRet != 0):
            print("getFrame fail! timeOut [500]ms")
            # 释放相关资源
            # release stream source object before return
            streamSource.contents.release(streamSource)
            continue
        stRecordFrameInfoParam.data = frame.contents.getImage(frame)
        stRecordFrameInfoParam.size = frame.contents.getImageSize(frame)
        stRecordFrameInfoParam.nPaddingX = frame.contents.getImagePaddingX(frame)
        stRecordFrameInfoParam.nPaddingY = frame.contents.getImagePaddingY(frame)
        stRecordFrameInfoParam.pixelformat = frame.contents.getImagePixelFormat(frame)
        # 录制一帧图像
        # record one frame
        nRet = RecordVideodll.inputOneFrame(handle, byref(stRecordFrameInfoParam))
        if nRet == 0:
            imageCount = imageCount+1
            print("record frame %d successfully " % imageCount)
        else:
            print("record frame failed data %d" % nRet)
        ret = frame.contents.release(frame)
        if 0 != ret:
            print("release frame failed errorcode[%d]\n" % ret)

if __name__=="__main__":
    nRet = record()
    if nRet != 0:
        print("Some Error happend")
    print("--------- Record end ---------")

