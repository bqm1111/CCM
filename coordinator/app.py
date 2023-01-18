import urllib

import models
import schema
from database import Base, SessionLocal, engine
from fastapi import Depends, FastAPI, HTTPException, status
from flask import jsonify
from pydantic.typing import List
from sqlalchemy import and_
from sqlalchemy.exc import MultipleResultsFound, NoResultFound
from sqlalchemy.orm import Session, joinedload

Base.metadata.create_all(engine)
app = FastAPI(title="Camera")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

############################### CAMERA ############################################################
@app.post("/Cameras", response_model=schema.CameraBase, status_code=status.HTTP_201_CREATED)
async def add_camera(cameraInfo: schema.CameraCreate, db: Session = Depends(get_db)):
    new_camera = models.Camera(ip_address = cameraInfo.ip_address, 
                               camera_id = cameraInfo.camera_id,
                                username=cameraInfo.username,
                                password=cameraInfo.password,
                                encodeType=cameraInfo.encodeType,
                                type=cameraInfo.type,
                                width=cameraInfo.witdh,
                                height=cameraInfo.height)
    db.add(new_camera)
    db.commit()
    db.refresh(new_camera)
    db.close()
    
    return new_camera

@app.put("/Cameras/{id}", response_model=schema.CameraBase)
def update_camera_info(id: int, cameraInfo: schema.CameraCreate, session: Session = Depends(get_db)):

    camera = session.query(models.Camera).get(id)

    if camera:
        camera.camera_id = cameraInfo.camera_id
        camera.ip_address = cameraInfo.ip_address
        camera.username = cameraInfo.username
        camera.password = cameraInfo.password
        camera.encodeType = cameraInfo.encodeType
        camera.type = cameraInfo.type
        camera.width = cameraInfo.width
        camera.height = cameraInfo.height

        session.commit()

    if not camera:
        raise HTTPException(status_code=404, detail=f"camera item with id {id} not found")

    return camera

@app.delete("/Cameras/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_camera(id: int, session: Session = Depends(get_db)):
    camera = session.query(models.Camera).get(id)

    if camera:
        session.delete(camera)
        session.commit()
    else:
        raise HTTPException(status_code=404, detail=f"camera item with id {id} not found")

    return None

############################### AGENT ############################################################
@app.post("/Agents", response_model=schema.AgentBase, status_code=status.HTTP_201_CREATED)
async def add_agent(agentInfo: schema.AgentCreate, db: Session = Depends(get_db)):
    new_agent = models.Agent(ip_address=agentInfo.ip_address,
                             node_id=agentInfo.node_id,
                             hostname=agentInfo.hostname,
                             agent_name=agentInfo.agent_name,
                             connected=agentInfo.connected)
    db.add(new_agent)
    db.commit()
    db.refresh(new_agent)
    db.close()
    
    return new_agent

@app.put("/Agents/{id}", response_model=schema.AgentBase)
def update_camera_info(id: int, agentInfo: schema.AgentCreate, session: Session = Depends(get_db)):
    agent = session.query(models.Agent).get(id)

    if agent:
        agent.ip_address = agentInfo.ip_address
        agent.hostname = agentInfo.hostname
        agent.node_id = agentInfo.node_id
        agent.agent_name = agentInfo.agent_name
        agent.connected = agentInfo.agent_name
        session.commit()

    if not agent:
        raise HTTPException(status_code=404, detail=f"agent item with id {id} not found")

    return agent

@app.delete("/Agents/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_camera(id: int, session: Session = Depends(get_db)):
    agent = session.query(models.Agent).get(id)

    if agent:
        session.delete(agent)
        session.commit()
    else:
        raise HTTPException(status_code=404, detail=f"agent item with id {id} not found")

    return None

############################### DSINSTANCE ############################################################
@app.post("/DsInstance", response_model=schema.DsInstanceBase, status_code=status.HTTP_201_CREATED)
async def add_agent(instanceInfo: schema.DsInstanceCreate, db: Session = Depends(get_db)):
    new_agent = models.DsInstance(instance_name=instanceInfo.instance_name,
                             app_type=instanceInfo.app_type,
                             face_raw_meta_topic=instanceInfo.face_raw_meta_topic,
                             mot_raw_meta_topic=instanceInfo.mot_raw_meta_topic,
                             visual_topic=instanceInfo.visual_topic,
                             kafka_connection_str=instanceInfo.kafka_connection_str,
                             streammux_output_width=instanceInfo.streammux_output_width,
                             streammux_output_height=instanceInfo.streammux_output_height,
                             streammux_batch_size=instanceInfo.streammux_batch_size,
                             streammux_buffer_pool=instanceInfo.streammux_buffer_pool,
                             streammux_nvbuf_memory_type=instanceInfo.streammux_nvbuf_memory_type,
                             face_confidence_threshold=instanceInfo.face_confidence_threshold,
                             )
    db.add(new_agent)
    db.commit()
    db.refresh(new_agent)
    db.close()
    
    return new_agent

@app.put("/DsInstance/{id}", response_model=schema.DsInstanceBase)
def update_camera_info(id: int, instanceInfo: schema.DsInstanceCreate, session: Session = Depends(get_db)):
    instance = session.query(models.DsInstance).get(id)

    if instance:
        instance.instance_name=instanceInfo.instance_name
        instance.app_type=instanceInfo.app_type
        instance.face_raw_meta_topic=instanceInfo.face_raw_meta_topic
        instance.mot_raw_meta_topic=instanceInfo.mot_raw_meta_topic
        instance.visual_topic=instanceInfo.visual_topic,
        instance.kafka_connection_str=instanceInfo.kafka_connection_str
        instance.streammux_output_width=instanceInfo.streammux_output_width
        instance.streammux_output_height=instanceInfo.streammux_output_height
        instance.streammux_batch_size=instanceInfo.streammux_batch_size
        instance.streammux_buffer_pool=instanceInfo.streammux_buffer_pool
        instance.streammux_nvbuf_memory_type=instanceInfo.streammux_nvbuf_memory_type
        instance.face_confidence_threshold=instanceInfo.face_confidence_threshold   
        
        session.commit()

    if not instance:
        raise HTTPException(status_code=404, detail=f"DsInstance item with id {id} not found")

    return instance

@app.delete("/DsInstance/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_camera(id: int, session: Session = Depends(get_db)):
    instance = session.query(models.DsInstance).get(id)

    if instance:
        session.delete(instance)
        session.commit()
    else:
        raise HTTPException(status_code=404, detail=f"DsInstance item with id {id} not found")

    return None


############################### CAMERA_AGENT ############################################################

@app.put("/Camera_Agents", response_model=schema.CameraBase, status_code=status.HTTP_201_CREATED)
async def add_camera_agent_association(agent_ip: str, camera_ip: str, db: Session = Depends(get_db)):
    try:
        agent = db.query(models.Agent).where(models.Agent.ip_address == agent_ip).one()
    except MultipleResultsFound:
        raise HTTPException(status_code=400, detail=f"Multiple Agent item with ip_address {agent_ip} are found. Please provide more information")
    except NoResultFound:
        raise HTTPException(status_code=404, detail=f"Agent item with ip_address {agent_ip} not found")
    
    try:        
        camera = db.query(models.Camera).where(models.Camera.ip_address == camera_ip).one()
    except MultipleResultsFound:
        raise HTTPException(status_code=400, detail=f"Multiple camera item with ip_address {camera_ip} are found. Please provide more information")
    except NoResultFound:
        raise HTTPException(status_code=404, detail=f"camera item with ip_address {camera_ip} not found")

    camera.agent_id = agent.id
    db.commit()
    
    return camera

############################### CAMERA_INSTANCE ############################################################

@app.put("/Camera_Instance", response_model=schema.CameraBase, status_code=status.HTTP_201_CREATED)
async def add_camera_instance_association(instance_name: str, camera_ip: str, db: Session = Depends(get_db)):
    
    try:
        dsInstance = db.query(models.DsInstance).where(models.DsInstance.instance_name == instance_name).one()
    except MultipleResultsFound:
        raise HTTPException(status_code=400, detail=f"Multiple DsInstance item with name {instance_name} are found. Please provide more information")
    except NoResultFound:
        raise HTTPException(status_code=404, detail=f"DsInstance item with name {instance_name} not found")
    
    try:        
        camera = db.query(models.Camera).where(models.Camera.ip_address == camera_ip).one()
    except MultipleResultsFound:
        raise HTTPException(status_code=400, detail=f"Multiple camera item with ip_address {camera_ip} are found. Please provide more information")
    except NoResultFound:
        raise HTTPException(status_code=404, detail=f"camera item with ip_address {camera_ip} not found")
    
    camera.dsInstance_id = dsInstance.id
    db.commit()
    db.close()
    
    return camera

############################### AGENT_INSTANCE ############################################################

@app.put("/Agent_Instance", response_model=schema.DsInstanceBase, status_code=status.HTTP_201_CREATED)
async def add_agent_instance_association(agent_ip: str, instance_name: str, db: Session = Depends(get_db)):
    try:
        agent = db.query(models.Agent).where(models.Agent.ip_address == agent_ip).one()
    except MultipleResultsFound:
        raise HTTPException(status_code=400, detail=f"Multiple Agent item with ip_address {agent_ip} are found. Please provide more information")
    except NoResultFound:
        raise HTTPException(status_code=404, detail=f"Agent item with ip_address {agent_ip} not found")
    
    try:
        dsInstance = db.query(models.DsInstance).where(models.DsInstance.instance_name == instance_name).one()
    except MultipleResultsFound:
        raise HTTPException(status_code=400, detail=f"Multiple DsInstance item with name {instance_name} are found. Please provide more information")
    except NoResultFound:
        raise HTTPException(status_code=404, detail=f"DsInstance item with name {instance_name} not found")
    
    dsInstance.agent_id = agent.id
    db.commit()
    db.close()
    
    return dsInstance


def create_sample_database(db: Session):
    camera1 = models.Camera(camera_id=3, ip_address="172.21.111.101", username="admin", 
                            password="123456a@", encodeType="h265", type="rtsp", width=3840, height=2160)
    camera2 = models.Camera(camera_id=1, ip_address="172.21.111.104", username="admin", 
                            password="123456a@", encodeType="h265", type="rtsp", width=3840, height=2160)
    camera3 = models.Camera(camera_id=2, ip_address="172.21.111.111", username="admin", 
                            password="123456a@", encodeType="h265", type="rtsp", width=3840, height=2160)
    camera4 = models.Camera(camera_id=4, ip_address="172.21.104.112", username="admin", 
                            password="123456a@", encodeType="h265", type="rtsp", width=3840, height=2160)
    
    agent1 = models.Agent(agent_name="VTX", ip_address="172.21.100.242")
    agent2 = models.Agent(agent_name="VHT", ip_address="172.21.100.167")
    
    dsInstance1 = models.DsInstance(instance_name="deepstream-VTX", 
                                   app_type="NORMAL",
                                   face_raw_meta_topic="RawFaceMeta",
                                   mot_raw_meta_topic="RawMotMeta",
                                   visual_topic="RawImage",
                                   kafka_connection_str="172.21.100.242:9092",
                                   streammux_output_width=3840,
                                   streammux_output_height=2160,
                                   streammux_batch_size=4,
                                   streammux_buffer_pool=40,
                                   streammux_nvbuf_memory_type=3,
                                   face_confidence_threshold=0.1)
    dsInstance2 = models.DsInstance(instance_name="deepstream-VHT", 
                                   app_type="NORMAL",
                                   face_raw_meta_topic="RawFaceMeta",
                                   mot_raw_meta_topic="RawMotMeta",
                                   visual_topic="RawImage",
                                   kafka_connection_str="172.21.100.242:9092",
                                   streammux_output_width=3840,
                                   streammux_output_height=2160,
                                   streammux_batch_size=4,
                                   streammux_buffer_pool=40,
                                   streammux_nvbuf_memory_type=3,
                                   face_confidence_threshold=0.1)

    data = [camera1, camera2, camera3, camera4, agent1, agent2, dsInstance1, dsInstance2]
    for cam in data:
        db.add(cam)
        db.commit()
        db.refresh(cam)
    db.close()


if __name__ == '__main__':
    db = Session(bind=engine)
    # create_sample_database(db)  
    from schemas.config_schema import (DsAppConfig, DsInstanceConfig,
                                   FACE_align_config, FACE_pgie_config,
                                   FACE_sgie_config, MOT_pgie_config,
                                   MOT_sgie_config, SingleSourceConfig,
                                   SourcesConfig, parse_txt_as)
    from schemas.topic_schema import NodeInfo, DsInstance
    from pydantic import UUID4
    import json, uuid
    agent_info_list = []
    for agent in db.query(models.Agent).options(joinedload(models.Agent.dsInstance)).all():
        if not agent.connected:
            continue
        hostname = agent.hostname
        node_id = uuid.UUID(agent.node_id)
        instance_info_list = []
        for dsInstance in agent.dsInstance:
            cameras = db.query(models.Camera).where(models.Camera.dsInstance_id == dsInstance.id).all()
            source_list = []
            for camera in cameras:
                cam = db.query(models.Camera).get(camera.camera_id)
                url_password = urllib.parse.quote_plus(cam.password)
                rtsp_address = "rtsp://" + cam.username + ":" + url_password + "@" + cam.ip_address + "/main"
                source = dict()
                source["camera_id"] = cam.camera_id
                source["address"] = rtsp_address
                source["encode_type"] = cam.encodeType
                source["type"] = cam.type
                source_list.append(SingleSourceConfig.parse_obj(source))
            source_conf = SourcesConfig(sources=source_list)
            app_config = dsInstance.to_app_conf_dict()
            app_conf = DsAppConfig.parse_obj(app_config)
            
            with open("../sample_configs/faceid_primary.txt") as f:
                face_pgie_json, _ = parse_txt_as(FACE_pgie_config, f.read())
            with open("../sample_configs/mot_primary.txt") as f:
                mot_pgie_json, _ = parse_txt_as(MOT_pgie_config, f.read())

            with open("../sample_configs/faceid_secondary.txt") as f:
                face_sgie_json, _ = parse_txt_as(FACE_sgie_config, f.read())

            with open("../sample_configs/mot_sgie.txt") as f:
                mot_sgie_json, _ = parse_txt_as(MOT_sgie_config, f.read())

            with open("../sample_configs/faceid_align_config.txt") as f:
                face_align_json, _ = parse_txt_as(FACE_align_config, f.read())
            
            face_pgie_conf = FACE_pgie_config.parse_obj(face_pgie_json)
            face_sgie_conf = FACE_sgie_config.parse_obj(face_sgie_json)
            face_align_conf = FACE_align_config.parse_obj(face_align_json)
            mot_pgie_conf = MOT_pgie_config.parse_obj(mot_pgie_json)
            mot_sgie_conf = MOT_sgie_config.parse_obj(mot_sgie_json)
            instance_config = DsInstanceConfig(appconfig=app_conf, 
                                    sourceconfig=source_conf,
                                    face_pgie=face_pgie_conf,
                                    face_sgie=face_sgie_conf,
                                    face_align=face_align_conf,
                                    mot_pgie=mot_pgie_conf,
                                    mot_sgie=mot_sgie_conf)
            
            instance_info_list.append(DsInstance(name=dsInstance.instance_name,
                                                 config=instance_config))
            print(instance_info_list)
        agent_info_list.append(NodeInfo(hostname=hostname,
                                        node_id=node_id,
                                        node_config_list=instance_info_list))
    
    print((agent_info_list[0].node_config_list))

        
    
    
