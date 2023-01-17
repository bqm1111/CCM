from dataclasses import dataclass

from database import Base
from flask import Flask, jsonify
from sqlalchemy import (Boolean, Column, Float, ForeignKey, Integer, String,
                        Table)
from sqlalchemy.orm import relationship

from common.datatype import EncodeType, SourceType


# Declare Classes / Tables
class CameraAgent(Base):
    __tablename__ = 'camera_agent'
    camera_id = Column(ForeignKey('cameras.id'), primary_key=True, ondelete='CASCADE')
    agent_id = Column(ForeignKey('agents.id'), primary_key=True, ondelete='CASCADE')
    camera = relationship("Camera", back_populates="agent")
    agent = relationship("Agent", back_populates="camera")

class CameraInstance(Base):
    __tablename__ = 'camera_instance'
    camera_id = Column(ForeignKey('cameras.id'), primary_key=True)
    instance_id = Column(ForeignKey('dsInstance.id'), primary_key=True)
    camera = relationship("Camera", back_populates="dsInstance")
    dsInstance = relationship("DsInstance", back_populates="camera")

class AgentInstance(Base):
    __tablename__ = 'agent_instance'
    agent_id = Column(ForeignKey('agents.id'), primary_key=True)
    instance_id = Column(ForeignKey('dsInstance.id'), primary_key=True)
    agent = relationship("Agent", back_populates="dsInstance")
    dsInstance = relationship("DsInstance", back_populates="agent")

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
    width = Column(Integer, nullable=True)
    height = Column(Integer, nullable=True)
    agent = relationship("CameraAgent", back_populates="camera")
    dsInstance = relationship("CameraInstance", back_populates="camera")

class Agent(Base):
    __tablename__ = 'agents'
    id = Column(Integer, primary_key=True)
    agent_name = Column(String, nullable=False)
    ip_address = Column(String, nullable=False)
    hostname = Column(String, nullable=True)
    node_id = Column(String, nullable=True)
    connected = Column(Boolean, nullable=True)
    camera = relationship("CameraAgent", back_populates="agent")
    dsInstance = relationship("AgentInstance", back_populates="agent")
    

class DsInstance(Base):
    __tablename__ = 'dsInstance'
    id = Column(Integer, primary_key=True)
    instance_name = Column(String, nullable=True)
    app_type = Column(String, nullable=False)
    face_raw_meta_topic = Column(String, nullable=True)
    mot_raw_meta_topic = Column(String, nullable=True)
    visual_topic = Column(String, nullable=True)
    kafka_connection_str = Column(String, nullable=True)
    streammux_output_width = Column(Integer, nullable=True)
    streammux_output_height = Column(Integer, nullable=True)
    streammux_batch_size = Column(Integer, nullable=True)
    streammux_buffer_pool = Column(Integer, nullable=True)
    streammux_nvbuf_memory_type = Column(Integer, nullable=True)
    face_confidence_threshold = Column(Float, nullable=True)
    camera = relationship("CameraInstance", back_populates="dsInstance")
    agent = relationship("AgentInstance", back_populates="dsInstance")