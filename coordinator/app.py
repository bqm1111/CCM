import urllib

import models
import schema
from database import Base, SessionLocal, engine
from fastapi import Depends, FastAPI, HTTPException, status
from flask import jsonify
from pydantic.typing import List
from sqlalchemy import and_
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
@app.get("/Cameras/{id}", response_model=schema.CameraSchema)
async def get_Camera(id: int, db: Session = Depends(get_db)):
    db_Camera = db.query(models.Camera).options(joinedload(models.Camera.agents)).\
        where(models.Camera.id == id).one()
    return db_Camera


@app.get("/Cameras", response_model=List[schema.CameraSchema])
async def get_Cameras(db: Session = Depends(get_db)):
    db_Cameras = db.query(models.Camera).options(joinedload(models.Camera.agents)).all()
    return db_Cameras

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
        camera_agent = session.query(models.CameraAgent).where(models.CameraAgent.camera_id == camera.id).all()
        for ca in camera_agent:
            session.delete(ca)
            session.commit()
        camera_instance = session.query(models.CameraInstance).where(models.CameraInstance.camera_id == camera.id).all()
        for ci in camera_instance:
            session.delete(ci)
            session.commit()
        session.delete(camera)
        session.commit()
    else:
        raise HTTPException(status_code=404, detail=f"camera item with id {id} not found")

    return None

############################### AGENT ############################################################

@app.get("/Agents/{id}", response_model=schema.AgentSchema)
async def get_Agent(id: int, db: Session = Depends(get_db)):
    db_Agent = db.query(models.Agent).options(joinedload(models.Agent.camera)).\
        where(models.Agent.id == id).one()
    return db_Agent


@app.get("/Agents", response_model=List[schema.AgentSchema])
async def get_Agents(db: Session = Depends(get_db)):
    db_Agents = db.query(models.Agent).options(joinedload(models.Agent.camera)).all()
    return db_Agents

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
        camera_agent = session.query(models.CameraAgent).where(models.CameraAgent.agent_id == agent.id).all()
        for ca in camera_agent:
            session.delete(ca)
            session.commit()
        agent_instance = session.query(models.AgentInstance).where(models.AgentInstance.agent_id == agent.id).all()
        for ai in agent_instance:
            session.delete(ai)
            session.commit()

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
        agent_instance = session.query(models.AgentInstance).where(models.AgentInstance.instance_id == instance.id).all()
        for ai in agent_instance:
            session.delete(ai)
            session.commit()
            
        camera_instance = session.query(models.CameraInstance).where(models.CameraInstance.instance_id == instance.id).all()
        for ci in camera_instance:
            session.delete(ci)
            session.commit()

        session.delete(instance)
        session.commit()
    else:
        raise HTTPException(status_code=404, detail=f"DsInstance item with id {id} not found")

    return None


############################### CAMERA_AGENT ############################################################

@app.post("/Camera_Agents", response_model=schema.CameraAgentBase, status_code=status.HTTP_201_CREATED)
async def add_camera_agent_association(agent_ip: str, camera_ip: str, db: Session = Depends(get_db)):
    
    agent = db.query(models.Agent).where(models.Agent.ip_address == agent_ip).one()
    camera = db.query(models.Camera).where(models.Camera.ip_address == camera_ip).one()
    
    camera_agent = models.CameraAgent(camera_id=camera.id, agent_id=agent.id)
    db.add(camera_agent)
    db.commit()
    db.refresh(camera_agent)
    db.close()
    
    return camera_agent

@app.delete("/Camera_Agents/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_camera_agent_association(agent_id: int, camera_id: int, session: Session = Depends(get_db)):

    camera_agent = session.query(models.CameraAgent).where(and_(
                                                            models.CameraAgent.agent_id == agent_id,
                                                            models.CameraAgent.camera_id == camera_id)).one()

    if camera_agent:
        session.delete(camera_agent)
        session.commit()
    else:
        raise HTTPException(status_code=404, detail=f"camera item with id {id} not found")

    return None

############################### CAMERA_INSTANCE ############################################################

@app.post("/Camera_Instance", response_model=schema.CameraInstanceBase, status_code=status.HTTP_201_CREATED)
async def add_camera_instance_association(agent_ip: str, camera_ip: str, db: Session = Depends(get_db)):
    
    agent = db.query(models.Agent).where(models.Agent.ip_address == agent_ip).one()
    camera = db.query(models.Camera).where(models.Camera.ip_address == camera_ip).one()
    
    camera_agent = models.CameraAgent(camera_id=camera.id, agent_id=agent.id)
    db.add(camera_agent)
    db.commit()
    db.refresh(camera_agent)
    db.close()
    
    return camera_agent

@app.delete("/Camera_Instance/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_camera_instance_association(agent_id: int, camera_id: int, session: Session = Depends(get_db)):

    camera_agent = session.query(models.CameraAgent).where(and_(
                                                            models.CameraAgent.agent_id == agent_id,
                                                            models.CameraAgent.camera_id == camera_id)).one()

    if camera_agent:
        session.delete(camera_agent)
        session.commit()
    else:
        raise HTTPException(status_code=404, detail=f"camera item with id {id} not found")

    return None

############################### AGENT_INSTANCE ############################################################

@app.post("/Camera_Agents", response_model=schema.CameraAgentBase, status_code=status.HTTP_201_CREATED)
async def add_camera_agent_association(agent_ip: str, camera_ip: str, db: Session = Depends(get_db)):
    
    agent = db.query(models.Agent).where(models.Agent.ip_address == agent_ip).one()
    camera = db.query(models.Camera).where(models.Camera.ip_address == camera_ip).one()
    
    camera_agent = models.CameraAgent(camera_id=camera.id, agent_id=agent.id)
    db.add(camera_agent)
    db.commit()
    db.refresh(camera_agent)
    db.close()
    
    return camera_agent

@app.delete("/Camera_Agents/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_camera_agent_association(agent_id: int, camera_id: int, session: Session = Depends(get_db)):

    # camera_agent = session.query(models.CameraAgent).where(and_(
    #                                                         models.CameraAgent.agent_id == agent_id,
    #                                                         models.CameraAgent.camera_id == camera_id)).one()

    # if camera_agent:
    #     session.delete(camera_agent)
    #     session.commit()
    # else:
    #     raise HTTPException(status_code=404, detail=f"camera item with id {id} not found")

    return None


def create_sample_database(db: Session):
    camera1 = models.Camera(camera_id=3, ip_address="172.21.111.101", username="admin", 
                            password="123456a@", encodeType="h265", type="rtsp", width=3840, height=2160)
    camera2 = models.Camera(camera_id=1, ip_address="172.21.111.104", username="admin", 
                            password="123456a@", encodeType="h265", type="rtsp", width=3840, height=2160)
    camera3 = models.Camera(camera_id=2, ip_address="172.21.111.111", username="admin", 
                            password="123456a@", encodeType="h265", type="rtsp", width=3840, height=2160)
    camera4 = models.Camera(camera_id=4, ip_address="172.21.104.112", username="admin", 
                            password="123456a@", encodeType="h265", type="rtsp", width=3840, height=2160)
    
    data = [camera1, camera2, camera3, camera4]
    for cam in data:
        db.add(cam)
        db.commit()
        db.refresh(cam)
    db.close()


if __name__ == '__main__':
    db = Session(bind=engine)
    # create_sample_database(db)  
    from schemas.config_schema import SingleSourceConfig, SourcesConfig
    agent_info_list = []
    for agent in db.query(models.Agent).options(joinedload(models.Agent.camera)).all():
        source_list = []
        hostname = agent.hostname
        for camera in agent.camera:
            cam = db.query(models.Camera).get(camera.camera_id)
            url_password = urllib.parse.quote_plus(cam.password)
            rtsp_address = "rtsp://" + cam.username + ":" + url_password + "@" + cam.ip_address + "/main"
            source = dict()
            source["camera_id"] = cam.camera_id
            source["address"] = rtsp_address
            source["encode_type"] = cam.encode_type
            source["type"] = cam.type
            source_list.append(SingleSourceConfig.parse_obj(source))
        source_conf = SourcesConfig(sources=source_list)


