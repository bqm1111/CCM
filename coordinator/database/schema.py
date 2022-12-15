from pydantic import BaseModel, Field

class AgentCreate(BaseModel):
    computer_id: str = Field(description="unique id of the computer running the agent program")
    ip_address: str = Field(description="ip address of the agent")

class AgentInfo(BaseModel):
    agent_id: int 
    computer_id: str = Field(description="unique id of the computer running the agent program")
    ip_address: str = Field(description="ip address of the agent")
