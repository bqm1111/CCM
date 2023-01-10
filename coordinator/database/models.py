from enum import Enum, IntEnum

from database import Base
from sqlalchemy import Column, Integer, String, create_engine

from schemas.config_schema import DsAppMode, DsAppStatus


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
    