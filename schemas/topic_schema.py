from typing import List

from pydantic import UUID4, BaseModel, Field, IPvAnyAddress, NonNegativeInt

from schemas.config_schema import DsInstanceConfig
import subprocess
TOPIC200 = "AgentInfo"
TOPIC201 = "AgentCommand"
TOPIC210 = "AgentConfig"
TOPIC220 = "AgentResponse"

class DsInstance(BaseModel):
    name: str
    config: DsInstanceConfig

class NodeInfo(BaseModel):
    hostname: str
    node_id: UUID4
    node_config_list: List[DsInstance]

class InstanceStatus(BaseModel):
    pass

# 
class Topic200Model(BaseModel):
    """greeting from Agent to Coordinator"""

    message_id: UUID4
    agent_name: str
    ip: str
    capacity: NonNegativeInt = Field(description="number of camera this machine can handle")
    gpulist: List[str]
    description: str = ""
    class Config:
        title = "AgentInfo"


class Topic201Model(BaseModel):
    """response from Coordianator to Agent"""

    message_id: UUID4
    agent_name: str
    agent_id: UUID4  # Agent must save its id
    class Config:
        title = "AgentCommand"


class TOPIC210Model(BaseModel):
    """Announce new configuration for agents"""  
    agent_info_list: List[NodeInfo]
    class Config:
        title = "AgentConfig"


class Topic220Model(BaseModel):
    """update status of Agent to Coordinator"""

    agent_id: UUID4
    status: List[InstanceStatus]
    class Config:
        title = "AgentResponse"

if __name__ == "__main__":
    # print(IPvAnyAddress("12,42.423"))
    p = subprocess.run(["cat", "/etc/machine-id"], capture_output=True)

    print(UUID4(p.stdout.decode().rstrip()))
    # ip = 172.21.100.234
    # print(IPvAnyAddress(ip))