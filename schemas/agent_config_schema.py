import re
import os
from enum import Enum, IntEnum
from pydantic import BaseModel, Field

class DsAppStatus(IntEnum):
    RUNNING = 1
    STOPPED = 0
    
class DsAppMode(IntEnum):
    DEBUG = 0
    RELEASE = 1


TOPIC200 = "AgentInfo"
TOPIC201 = "AgentCommand"
TOPIC210 = "AgentConfig"
TOPIC220 = "AgentResponse"


class TOPIC200Model(BaseModel):
    """Contain information of each agent"""    
    agent_id: str
    hostname: str
    ip_address: str
    
    class Config:
        title = "AgentInfo"

class TOPIC201Model(BaseModel):
    """Record to acknowledge the agent that it is allowed to enter the system"""
    allowed: bool
    
    class Config:
        title = "AgentCommand"

class TOPIC210Model(BaseModel):
    """Announce new configuration for agents"""   
    class Config:
        title = "AgentConfig"
        

class TOPIC220Model(BaseModel):
    """Response message of agent to coordinator"""
    class Config:
        title = "AgentResponse"

# 
