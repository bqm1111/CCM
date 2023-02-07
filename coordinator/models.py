import uuid

from database import Base
from sqlalchemy import (Boolean, Column, Float, ForeignKey, Integer, String,
                        Table)
from sqlalchemy.orm import relationship

from common.datatype import EncodeType, SourceType


# Declarative styles
class Camera(Base):
    __tablename__ = 'cameras'
    id = Column(Integer, primary_key=True)
    agent_id = Column(Integer, ForeignKey('agents.id'))
    dsInstance_id = Column(Integer, ForeignKey('dsInstance.id'))
    camera_id = Column(String, nullable=False)
    ip_address = Column(String, nullable=False)
    username = Column(String, nullable=True)
    password = Column(String, nullable=True)
    encodeType = Column(String, nullable=False)
    type = Column(String, nullable=False)
    width = Column(Integer, nullable=True)
    height = Column(Integer, nullable=True)
    agent = relationship("Agent", back_populates="camera")
    dsInstance = relationship("DsInstance", back_populates="camera")

class Agent(Base):
    __tablename__ = 'agents'
    id = Column(Integer, primary_key=True)
    agent_name = Column(String, nullable=False)
    ip_address = Column(String, nullable=False)
    hostname = Column(String, nullable=True)
    node_id = Column(String, nullable=True)
    connected = Column(Boolean, nullable=True)
    camera = relationship("Camera", back_populates="agent")
    dsInstance = relationship("DsInstance", back_populates="agent")
    

class DsInstance(Base):
    __tablename__ = 'dsInstance'
    id = Column(Integer, primary_key=True)
    agent_id = Column(Integer, ForeignKey('agents.id'))
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
    mot_confidence_threshold = Column(Float, nullable=True)
    status = Column(String, nullable=True)
    camera = relationship("Camera", back_populates="dsInstance")
    agent = relationship("Agent", back_populates="dsInstance")
    
    def to_app_conf_dict(self):
        app_config = {}
        app_config["app_type"] = self.app_type
        app_config["face_raw_meta_topic"] = self.face_raw_meta_topic
        app_config["mot_raw_meta_topic"] = self.mot_raw_meta_topic
        app_config["visual_topic"] = self.visual_topic
        app_config["kafka_connection_str"] = self.kafka_connection_str
        app_config["streammux_output_width"] = self.streammux_output_width
        app_config["streammux_output_height"] = self.streammux_output_height
        app_config["streammux_batch_size"] = self.streammux_batch_size
        app_config["streammux_buffer_pool"] = self.streammux_buffer_pool
        app_config["streammux_nvbuf_memory_type"] = self.streammux_nvbuf_memory_type
        app_config["face_confidence_threshold"] = self.face_confidence_threshold
        app_config["mot_confidence_threshold"] = self.mot_confidence_threshold
        return app_config
