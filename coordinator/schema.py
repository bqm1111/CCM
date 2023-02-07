from typing import Optional

from pydantic import BaseModel


class AgentCreate(BaseModel):
    agent_name: str
    ip_address: str
    hostname: str = ""
    node_id: str = ""
    connected: bool = False

class AgentBase(AgentCreate):
    id: int    
    class Config:
        orm_mode = True

class CameraCreate(BaseModel):
    camera_id: str
    ip_address: str
    username: str = "admin"
    password: str = "123456a@"
    encodeType: str = "h265"
    type: str = "rtsp"
    width: int = "3840"
    height: int = "2160"
    
    
class CameraBase(CameraCreate):
    id: int
    agent_id: Optional[int]
    dsInstance_id: Optional[int]
    class Config:
        orm_mode = True

class DsInstanceCreate(BaseModel):
    instance_name: str 
    app_type: str = "NORMAL"
    face_raw_meta_topic: str = "RawFaceMeta"
    mot_raw_meta_topic: str = "RawMotMeta"
    visual_topic: str = "RawImage"
    kafka_connection_str: str = "172.21.100.242:9092"
    streammux_output_width: int = 3840
    streammux_output_height: int = 2160
    streammux_batch_size: int = 4
    streammux_buffer_pool: int = 40
    streammux_nvbuf_memory_type: int = 3
    face_confidence_threshold: float = 0.6
    mot_confidence_threshold: float = 0.6
    status: str = ""

class DsInstanceBase(DsInstanceCreate):
    id: int
    agent_id: Optional[int]
    class Config:
        orm_mode = True
