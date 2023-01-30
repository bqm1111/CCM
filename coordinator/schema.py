from typing import Optional

from pydantic import BaseModel


class AgentCreate(BaseModel):
    agent_name: str
    ip_address: str
    hostname: str
    node_id: str
    connected: bool

class AgentBase(AgentCreate):
    id: int    
    class Config:
        orm_mode = True

class CameraCreate(BaseModel):
    camera_id: int
    ip_address: str
    username: str
    password: str
    encodeType: str
    type: str
    width: int
    height: int
    
    
class CameraBase(CameraCreate):
    id: int
    agent_id: Optional[int]
    dsInstance_id: Optional[int]
    class Config:
        orm_mode = True

class DsInstanceCreate(BaseModel):
    instance_name: str
    app_type: str
    face_raw_meta_topic: str
    mot_raw_meta_topic: str
    visual_topic: str
    kafka_connection_str: str
    streammux_output_width: int
    streammux_output_height: int
    streammux_batch_size: int
    streammux_buffer_pool: int 
    streammux_nvbuf_memory_type: int
    face_confidence_threshold: float
    status: str

class DsInstanceBase(DsInstanceCreate):
    id: int
    agent_id: Optional[int]
    class Config:
        orm_mode = True
