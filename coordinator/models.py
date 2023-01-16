from database import Base
from sqlalchemy import Column, ForeignKey, Integer, String, Table
from sqlalchemy.orm import relationship

from common.datatype import EncodeType, SourceType


# Declare Classes / Tables
class CameraAgent(Base):
    __tablename__ = 'camera_agent'
    camera_id = Column(ForeignKey('cameras.id'), primary_key=True)
    agent_id = Column(ForeignKey('agents.id'), primary_key=True)
    camera = relationship("Camera", back_populates="agent")
    agent = relationship("Agent", back_populates="camera")

# Declarative styles
class Camera(Base):
    __tablename__ = 'cameras'
    id = Column(Integer, primary_key=True)
    camera_id = Column(Integer, nullable=False)
    ip_address = Column(String, nullable=False)
    username = Column(String, nullable=True)
    password = Column(String, nullable=True)
    encodeType = Column(String, nullable=False)
    type = Column(String, nullable=False)
    agent = relationship("CameraAgent", back_populates="camera")

class Agent(Base):
    __tablename__ = 'agents'
    id = Column(Integer, primary_key=True)
    ip_address = Column(String, nullable=False)
    hostname = Column(String, nullable=True)
    node_id = Column(String, nullable=True)
    camera = relationship("CameraAgent", back_populates="agent")

