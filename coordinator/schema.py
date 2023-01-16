from pydantic import BaseModel
from pydantic.typing import List

from common.datatype import EncodeType, SourceType


class CameraAgentBase(BaseModel):
    camera_id: int
    agent_id: int     
    class Config:
        orm_mode = True


class AgentBase(BaseModel):
    id: int
    ip_address: str
    hostname: str
    node_id: str
    class Config:
        orm_mode = True

class AgentCreate(BaseModel):
    ip_address: str
    hostname: str
    node_id: str
    
class CameraBase(BaseModel):
    id: int
    camera_id: int
    ip_address: str
    username: str
    password: str
    encodeType: str
    type: str

    class Config:
        orm_mode = True

class CameraCreate(BaseModel):
    camera_id: int
    ip_address: str
    username: str
    password: str
    encodeType: str
    type: str

class CameraSchema(CameraBase):
    agents: List[AgentBase]

class AgentSchema(AgentBase):
    camera: List[CameraBase]
