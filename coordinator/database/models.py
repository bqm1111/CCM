from sqlalchemy import create_engine, Column, Integer, String
from database import Base 
from enum import Enum, IntEnum

class DsAppStatus(IntEnum):
    RUNNING = 1
    STOPPED = 0
    
class DsAppMode(IntEnum):
    DEBUG = 0
    RELEASE = 1
class Agent(Base):
    __tablename__ = "agent"
    agent_id = Column(Integer, primary_key=True)
    computer_id = Column(String(50))
    ip_address = Column(String(50))

class DsAppInstance(Base):
    __tablename__ = "DsAppInstance"
    status = Column(DsAppStatus)
    mode = Column(DsAppMode)
    running_time = Column(float)
    