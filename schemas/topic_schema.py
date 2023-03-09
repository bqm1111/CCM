import subprocess
from typing import List, Optional

from pydantic import UUID4, BaseModel, Field, IPvAnyAddress, NonNegativeInt, IPvAnyAddress

from schemas.config_schema import DsInstanceConfig

TOPIC200 = "AgentInfo"
TOPIC201 = "AgentCommand"
TOPIC210 = "AgentConfig"
TOPIC220 = "AgentResponse"
TOPIC222 = "ExitedInstance"
TOPIC300 = "UpdateConfig"
TOPIC301 = "Refresh"

class DsInstance(BaseModel):
    name: str
    config: DsInstanceConfig

class NodeInfo(BaseModel):
    hostname: str
    node_id: UUID4
    node_config_list: List[DsInstance]

class ExitedInstanceInfo(BaseModel):
    hostname: str
    node_id: UUID4
    exited_instance_name_list: List[str]
    
class InstanceStatus(BaseModel):
    instance_name: str
    state: str

class Topic200Model(BaseModel):
    """greeting from Agent to Coordinator"""

    node_id: UUID4
    hostname: str
    ip_address: IPvAnyAddress
    capacity: Optional[NonNegativeInt] = Field(description="number of camera this machine can handle")
    gpulist: Optional[List[str]]
    description: Optional[str] = ""
    class Config:
        title = "AgentInfo"


class Topic201Model(BaseModel):
    """response from Coordinator to Agent"""
    agent_name: str
    ip_address: IPvAnyAddress
    class Config:
        title = "AgentCommand"


class TOPIC210Model(BaseModel):
    """Announce new configuration for agents"""  
    agent_info_list: List[NodeInfo]
    class Config:
        title = "AgentConfig"


class Topic220Model(BaseModel):
    """update status of Agent to Coordinator"""

    node_id: UUID4
    status: List[InstanceStatus]
    class Config:
        title = "AgentResponse"

class Topic222Model(BaseModel):
    """list all exited instance in all agent"""
    exited_list: List[ExitedInstanceInfo]
    class Config:
        title = "ExitedInstance"
        
class Topic300Model(BaseModel):
    """Read config from database and send to all agents"""
    desc: str
    class Config:
        title = "UpdateConfig"

class Topic301Model(BaseModel):
    """Refresh"""
    desc: str
    class Config:
        title = "Refresh"

if __name__ == "__main__":
    p = subprocess.run(["cat", "/etc/machine-id"], capture_output=True)
    print(UUID4(p.stdout.decode().rstrip()))
