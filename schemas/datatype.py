from enum import Enum, IntEnum


class DsAppType(str, Enum):
    DEFAULT = "NORMAL"
    NORMAL = "NORMAL"
    VISUAL = "VISUAL"
    DEBUG = "VISUAL"

class EncodeType(str, Enum):
    H265 = "h265"
    H264 = "h264"

class SourceType(str, Enum):
    RTSP = "rtsp"
    FILE = "file"
    
class NetworkMode(IntEnum):
    FP32 = 0
    INT8 = 1
    FP16 = 2


class ProcessMode(IntEnum):
    PRIMARY = 1
    SECONDARY = 2


class NetworkType(IntEnum):
    DETECTOR = 0
    CLASSIFIER = 1
    SEGMENTATION = 2
    INSTANCE_SEGMENTATION = 3


class ClusterMode(IntEnum):
    GROUP_RECTANGLE = 0
    DBSCAN = 1
    NMS = 2
    DBSCAN_NMS = 3
    NONE = 4


class ModelColorFormat(IntEnum):
    RGB = 0
    BGR = 1
    GRAY = 2


class BoolEnum(IntEnum):
    FALSE = 0
    TRUE = 1

class TensorDataType(IntEnum):
    FP32 = 0
    UINT8 = 1
    INT8 = 2
    UINT32 = 3
    INT32 = 4
    FP16 = 5