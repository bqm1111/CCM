from typing import List
from pydantic import BaseModel, UUID4, IPvAnyAddress, NonNegativeInt, Field
from schemas.app_config_schema import InstanceConfig
from pydantic2ts import generate_typescript_defs


class NodeConfig(BaseModel):
    instances: List[InstanceConfig]


class InstanceStatus(BaseModel):
    pass


class Topic200Model(BaseModel):
    """greating from Agent to Coordinator"""

    message_id: UUID4
    agent_name: str
    ip: IPvAnyAddress
    capacity: NonNegativeInt = Field(description="number of camera this machine can handle")
    gpulist: List[str]
    description: str = ""


class Topic201Model(BaseModel):
    """response from Coordianator to Agent"""

    message_id: UUID4
    agent_name: str
    agent_id: UUID4  # Agent must save its id


class Topic210Model(BaseModel):
    target_agent_id: str
    node_config: NodeConfig


class Topic220Model(BaseModel):
    """update status of Agent to Coordinator"""

    agent_id: UUID4
    status: List[InstanceStatus]

if __name__ == "__main__":
    with open('schema_topic201.json', 'w') as _f:
        _f.write(Topic201Model.schema_json(indent=4))

    generate_typescript_defs("topic_schema", "topic_schema.ts")