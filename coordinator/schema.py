from pydantic import BaseModel
from pydantic.typing import List

from common.datatype import EncodeType, SourceType


class CameraAgentBase(BaseModel):
    camera_id: int
    agent_id: int     
    class Config:
        orm_mode = True

class CameraInstanceBase(BaseModel):
    camera_id: int
    instance_id: int     
    class Config:
        orm_mode = True
        
class AgentInstanceBase(BaseModel):
    instance_id: int
    agent_id: int     
    class Config:
        orm_mode = True


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

class DsInstanceBase(DsInstanceCreate):
    id: int
    class Config:
        orm_mode = True



class CameraSchema(CameraBase):
    agents: List[AgentBase]

class AgentSchema(AgentBase):
    camera: List[CameraBase]
