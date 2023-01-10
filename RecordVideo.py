#!/usr/bin/env python
# coding: utf-8
'''
Created on 2022-05-23

@author: 
'''
from ctypes import *

# 加载RecordVideo库
# load RecordVideo library
# 32bit
#RecordVideodll = OleDLL("../../../Runtime/Win32/RecordVideo.dll")
# 64bit
RecordVideodll = OleDLL("../../../Runtime/x64/RecordVideo.dll")

#定义枚举类型
#define enum type
def enum(**enums):
    return type('Enum', (), enums)

# RecordVideo.h => enum tagRECORD_EErr
RECORD_EErr = enum(
                        RECORD_SUCCESS=0,
                        RECORD_ILLEGAL_PARAM=1,
                        RECORD_ERR_ORDER=2,
                        RECORD_NO_MEMORY=3,
                        RECORD_NOT_SUPPORT=255
                   )

RECORD_EVideoFormatType = enum(
                                    RECORD_VIDEO_FMT_AVI=0,
                                    RECORD_VIDEO_FMT_NOT_SUPPORT=255
                                )

# RecordVideo.h => struct tagRECORD_SRecordParam
class RECORD_SRecordParam(Structure):
    _fields_ = [
                ('width', c_uint),
                ('height', c_uint),
                ('frameRate', c_float),
                ('quality', c_uint),
                ('recordFmtType', c_uint),
                ('recordFilePath', c_char_p),
                ('reserved', c_uint*26)
                ]

class RECORD_SFrameInfo(Structure):
    _fields_ = [
                ('data', c_char_p),
                ('size', c_uint),
                ('paddingX', c_uint),
                ('paddingY', c_uint),
                ('pixelformat', c_int),
                ('reserved', c_uint*27),
                ]

openRecord = RecordVideodll.openRecord

inputOneFrame = RecordVideodll.inputOneFrame

closeRecord = RecordVideodll.closeRecord
