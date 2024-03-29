import models
import schema
from database import Base, SessionLocal, engine
from fastapi import Depends, FastAPI, HTTPException, status
from pydantic.typing import List
from sqlalchemy.exc import MultipleResultsFound, NoResultFound
from sqlalchemy.orm import Session, joinedload
from confluent_kafka import Producer
from dynaconf import Dynaconf
import sys
sys.path.append("../")

from schemas.topic_schema import (Topic300Model,Topic301Model, Topic302Model, TOPIC302, TOPIC301, TOPIC300)
import uvicorn

Base.metadata.create_all(engine)
app = FastAPI(title="Camera")

settings = Dynaconf(settings_file='settings.toml')

BOOTSTRAP_SERVER = settings.BOOTSTRAP_SERVER
PRODUCER = Producer({'bootstrap.servers': BOOTSTRAP_SERVER})


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.on_event("shutdown")
async def shutdown_event():
    PRODUCER.flush()


@app.delete("/Database", status_code=status.HTTP_204_NO_CONTENT)
def delete_database(db: Session = Depends(get_db)):
    try:
        db.query(models.Agent).delete()
        db.query(models.DsInstance).delete()
        db.query(models.Camera).delete()
        db.commit()
    except:
        db.rollback()
    
    return {"detail": "Successfully deleted all records in database"}

############################### CAMERA ############################################################
@app.get("/Cameras/all_camera", status_code=status.HTTP_200_OK)
async def get_all_camera(db: Session = Depends(get_db)):
    camera = db.query(models.Camera).all()
    return camera

    
@app.post("/Cameras", response_model=schema.CameraBase, status_code=status.HTTP_201_CREATED)
async def add_camera(cameraInfo: schema.CameraCreate, db: Session = Depends(get_db)):
    try:
        _ = db.query(models.Camera).where(models.Camera.camera_id == cameraInfo.camera_id).one()
    except:
        try:
            _ = db.query(models.Camera).where(models.Camera.ip_address == cameraInfo.ip_address).one()
        except:
            new_camera = models.Camera(ip_address = cameraInfo.ip_address, 
                                    camera_id = cameraInfo.camera_id,
                                        username=cameraInfo.username,
                                        password=cameraInfo.password,
                                        encodeType=cameraInfo.encodeType,
                                        type=cameraInfo.type,
                                        stream=cameraInfo.stream,
                                        width=cameraInfo.width,
                                        height=cameraInfo.height)
            db.add(new_camera)
            db.commit()
            db.close()
        else:
            raise HTTPException(status_code=400, detail=f"Camera record with ip_address = {cameraInfo.ip_address} is already exist")
    else:
        raise HTTPException(status_code=400, detail=f"Camera record with camera_id = {cameraInfo.camera_id} is already exist")
    
    return new_camera


@app.put("/Cameras/{id}", response_model=schema.CameraBase)
async def update_camera_info(id: int, cameraInfo: schema.CameraCreate, db: Session = Depends(get_db)):
    camera = db.query(models.Camera).get(id)

    if camera:
        existed_cam = db.query(models.Camera).where(models.Camera.camera_id == cameraInfo.camera_id).all()
        if len(existed_cam) > 0:
            if existed_cam[0].id != id:
                raise HTTPException(status_code=400, detail=f"Camera record with camera_id = {cameraInfo.camera_id} is already exist")
            
        existed_cam = db.query(models.Camera).where(models.Camera.ip_address == cameraInfo.ip_address).all()
        if len(existed_cam) > 0:
            if existed_cam[0].id != id:
                raise HTTPException(status_code=400, detail=f"Camera record with ip_address = {cameraInfo.ip_address} is already exist")
        camera.camera_id = cameraInfo.camera_id
        camera.ip_address = cameraInfo.ip_address
        camera.username = cameraInfo.username
        camera.password = cameraInfo.password
        camera.encodeType = cameraInfo.encodeType
        camera.type = cameraInfo.type
        camera.stream = cameraInfo.stream
        camera.width = cameraInfo.width
        camera.height = cameraInfo.height

        db.commit()
        db.close()
    else:
        raise HTTPException(status_code=404, detail=f"camera item with id {id} not found")

    return camera


@app.delete("/Cameras/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_camera(id: int, session: Session = Depends(get_db)):
    camera = session.query(models.Camera).get(id)

    if camera:
        session.delete(camera)
        session.commit()
        session.close()
    else:
        raise HTTPException(status_code=404, detail=f"camera item with id {id} not found")

    return {f"Successfully deleted camera record with id = {id}"}

############################### AGENT ############################################################
@app.get("/Agent/get_dsInstance", status_code=status.HTTP_200_OK)
async def get_dsInstance_from_agent(agent_ip: str, db: Session = Depends(get_db)):
    try:
        agent = db.query(models.Agent).where(models.Agent.ip_address == agent_ip).one()
    except:
        raise HTTPException(status_code=400, detail=f"Cannot found agent named {agent_ip} in database")    
    else:
        try:
            instance = db.query(models.DsInstance).where(models.DsInstance.agent_id == agent.id).all()
        except:
            raise HTTPException(status_code=400, detail=f"No dsInstance was assigned to agent with ip address {agent_ip} in database")    
        else:
            return instance


@app.get("/Agent/all_agent")
async def get_all_agent(db: Session = Depends(get_db)):
    agent = db.query(models.Agent).all()
    return agent


@app.post("/Agents", response_model=schema.AgentBase, status_code=status.HTTP_201_CREATED)
async def add_agent(agentInfo: schema.AgentCreate, db: Session = Depends(get_db)):
    try:
        _ = db.query(models.Agent).where(models.Agent.ip_address == agentInfo.ip_address).one()
    except:
        new_agent = models.Agent(ip_address=agentInfo.ip_address,
                                node_id=agentInfo.node_id,
                                hostname=agentInfo.hostname,
                                agent_name=agentInfo.agent_name,
                                connected=agentInfo.connected)
        db.add(new_agent)
        db.commit()
        db.close()
    else:
        raise HTTPException(status_code=400, detail=f"Agent record with ip_address = {agentInfo.ip_address} is already exist")
    
    return new_agent

@app.put("/Agents/{id}", response_model=schema.AgentBase)
async def update_agent_info(id: int, agentInfo: schema.AgentCreate, db: Session = Depends(get_db)):
    agent = db.query(models.Agent).get(id)
    
    if agent:
        existed_agent = db.query(models.Agent).where(models.Agent.ip_address == agentInfo.ip_address).all()
        if len(existed_agent) > 0:
            if existed_agent[0].id != id:
                raise HTTPException(status_code=400, detail=f"Agent record with ip_address = {agentInfo.ip_address} is already exist")
                
        agent.ip_address = agentInfo.ip_address
        agent.hostname = agentInfo.hostname
        agent.node_id = agentInfo.node_id
        agent.agent_name = agentInfo.agent_name
        agent.connected = agentInfo.connected
        db.commit()
        db.close()
    else:
        raise HTTPException(status_code=404, detail=f"agent item with id {id} not found")

    return agent


@app.delete("/Agents/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_agent(id: int, session: Session = Depends(get_db)):
    agent = session.query(models.Agent).get(id)

    if agent:
        session.delete(agent)
        session.commit()
        session.close()
    else:
        raise HTTPException(status_code=404, detail=f"agent item with id {id} not found")

    return {f"Successfully deleted agent record with id = {id}"}

############################### DSINSTANCE ############################################################
@app.get("/DsInstance/get_camera", status_code=status.HTTP_200_OK)
async def get_camera_from_instance(instance_name: str, db: Session = Depends(get_db)):
    try:
        instance = db.query(models.DsInstance).where(models.DsInstance.instance_name == instance_name).one()
    except:
        raise HTTPException(status_code=404, detail=f"Cannot found instance named {instance_name} in database")    
    else:
        try:
            camera = db.query(models.Camera).where(models.Camera.dsInstance_id == instance.id).all()
        except:
            raise HTTPException(status_code=404, detail=f"No camera was assigned to instance named {instance_name} in database")    
        else:
            return camera


@app.get("/DsInstance/all_instance", status_code=status.HTTP_200_OK)
async def get_all_dsInstance(db: Session = Depends(get_db)):
    instance = db.query(models.DsInstance).all()
    return instance


@app.get("/DsInstance/get_instance_info", status_code=status.HTTP_200_OK)
async def get_instance_info(instance_name: str, db: Session = Depends(get_db)):
    try:
        instance = db.query(models.DsInstance).where(models.DsInstance.instance_name == instance_name).one()
    except:
        raise HTTPException(status_code=404, detail=f"Instance named {instance_name} is not found in database")    
    else:
        return instance


@app.post("/DsInstance", response_model=schema.DsInstanceBase, status_code=status.HTTP_201_CREATED)
async def add_dsInstance(instanceInfo: schema.DsInstanceCreate, db: Session = Depends(get_db)):
    try:
        _ = db.query(models.DsInstance).where(models.DsInstance.instance_name == instanceInfo.instance_name).one()
    except:
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
                                mot_confidence_threshold=instanceInfo.mot_confidence_threshold,
                                gpu_id=instanceInfo.gpu_id,
                                status=instanceInfo.status
                                )
        db.add(new_agent)
        db.commit()
        db.close()
    else:
        raise HTTPException(status_code=400, detail=f"DsInstance record with instance_name = {instanceInfo.instance_name} is already exist")
    
    return new_agent


@app.put("/DsInstance/{id}", response_model=schema.DsInstanceBase)
def update_dsInstance_info(id: int, instanceInfo: schema.DsInstanceCreate, db: Session = Depends(get_db)):
    instance = db.query(models.DsInstance).get(id)

    if instance:
        existed_instance = db.query(models.DsInstance).where(models.DsInstance.instance_name == instanceInfo.instance_name).all()
        if len(existed_instance) > 0:
            if existed_instance[0].id != id:
                raise HTTPException(status_code=400, detail=f"DsInstance record with instance_name = {instanceInfo.instance_name} is already exist")

        instance.instance_name=instanceInfo.instance_name
        instance.app_type=instanceInfo.app_type
        instance.face_raw_meta_topic=instanceInfo.face_raw_meta_topic
        instance.mot_raw_meta_topic=instanceInfo.mot_raw_meta_topic
        instance.visual_topic=instanceInfo.visual_topic
        instance.kafka_connection_str=instanceInfo.kafka_connection_str
        instance.streammux_output_width=instanceInfo.streammux_output_width
        instance.streammux_output_height=instanceInfo.streammux_output_height
        instance.streammux_batch_size=instanceInfo.streammux_batch_size
        instance.streammux_buffer_pool=instanceInfo.streammux_buffer_pool
        instance.streammux_nvbuf_memory_type=instanceInfo.streammux_nvbuf_memory_type
        instance.face_confidence_threshold=instanceInfo.face_confidence_threshold   
        instance.mot_confidence_threshold=instanceInfo.mot_confidence_threshold
        instance.gpu_id = instanceInfo.gpu_id
        db.commit()
        db.close()
    else:
        raise HTTPException(status_code=404, detail=f"DsInstance item with id {id} not found")

    return instance


@app.delete("/DsInstance/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_dsInstance(id: int, session: Session = Depends(get_db)):
    instance = session.query(models.DsInstance).get(id)

    if instance:
        session.delete(instance)
        session.commit()
        session.close()
    else:
        raise HTTPException(status_code=404, detail=f"DsInstance item with id {id} not found")

    return {f"Successfully deleted instance record with id = {id}"}



############################### CAMERA_AGENT ############################################################


@app.post("/Camera_Agents", status_code=status.HTTP_201_CREATED)
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
    db.close()
    
    return {"camera": camera, "agent": agent}


@app.put("/Camera_Agents", status_code=status.HTTP_201_CREATED)
async def remove_camera_agent_association(camera_ip: str, db: Session = Depends(get_db)):    
    try:        
        camera = db.query(models.Camera).where(models.Camera.ip_address == camera_ip).one()
    except MultipleResultsFound:
        raise HTTPException(status_code=400, detail=f"Multiple camera item with ip_address {camera_ip} are found. Please provide more information")
    except NoResultFound:
        raise HTTPException(status_code=404, detail=f"camera item with ip_address {camera_ip} not found")

    camera.agent_id = None
    db.commit()
    db.close()
    
    return {"camera": camera}

############################### CAMERA_INSTANCE ############################################################

@app.post("/Camera_Instance", status_code=status.HTTP_201_CREATED)
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
    
    return {"camera": camera, "instance": dsInstance}


@app.put("/Camera_Instance", status_code=status.HTTP_201_CREATED)
async def remove_camera_instance_association(camera_ip: str, db: Session = Depends(get_db)):    
    try:        
        camera = db.query(models.Camera).where(models.Camera.ip_address == camera_ip).one()
    except MultipleResultsFound:
        raise HTTPException(status_code=400, detail=f"Multiple camera item with ip_address {camera_ip} are found. Please provide more information")
    except NoResultFound:
        raise HTTPException(status_code=404, detail=f"camera item with ip_address {camera_ip} not found")
    
    camera.dsInstance_id = None
    db.commit()
    db.close()
    
    return {"camera": camera}


############################### AGENT_INSTANCE ############################################################

@app.post("/Agent_Instance", status_code=status.HTTP_201_CREATED)
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
    
    return {"agent": agent, "instance": dsInstance}


@app.put("/Agent_Instance", status_code=status.HTTP_201_CREATED)
async def remove_agent_instance_association(instance_name: str, db: Session = Depends(get_db)):    
    try:
        dsInstance = db.query(models.DsInstance).where(models.DsInstance.instance_name == instance_name).one()
    except MultipleResultsFound:
        raise HTTPException(status_code=400, detail=f"Multiple DsInstance item with name {instance_name} are found. Please provide more information")
    except NoResultFound:
        raise HTTPException(status_code=404, detail=f"DsInstance item with name {instance_name} not found")
    
    dsInstance.agent_id = None
    dsInstance.status = "Not assigned"
    db.commit()
    db.close()
    
    return {"instance": dsInstance}


@app.post("/Pause_Instance", status_code=status.HTTP_201_CREATED)
async def pause_instance(instance_name: str, db: Session = Depends(get_db)):
    try:
        instance = db.query(models.DsInstance).where(models.DsInstance.instance_name == instance_name).one()
    except:
        raise HTTPException(status_code=404, detail=f"Instance named {instance_name} is not found")
    else:
        if instance.agent_id is not None:
            agent = db.query(models.Agent).where(models.Agent.id == instance.agent_id).one()
        else:
            raise HTTPException(status_code=404, detail=f"Instance named {instance_name} is not assigned to any agent")

    PRODUCER.poll(0)
    PRODUCER.produce(TOPIC302, Topic302Model(instance_name=instance_name, node_id= agent.node_id).json())
    return {"Sent acknowlege message to TOPIC302"}


@app.post("/Update_config", status_code=status.HTTP_201_CREATED)
async def update_config():
    PRODUCER.poll(0)
    topic300data = Topic300Model(desc="UpdateConfig")
    PRODUCER.produce(TOPIC300, topic300data.json())
    return {"Sent acknowlege message to TOPIC300"}


@app.post("/Refresh", status_code=status.HTTP_201_CREATED)
async def refresh(db: Session = Depends(get_db)):
    agents = db.query(models.Agent).all()
    for agent in agents:
        agent.connected = False
    db.commit()
    db.close()
    
    PRODUCER.poll(0)
    topic301data = Topic301Model(desc="Refresh")
    PRODUCER.produce(TOPIC301, topic301data.json())
    return {"Sent acknowlege message to TOPIC301"}


def add_camera_from_file(db: Session):
    import csv
    with open("reachable.csv", "r") as f:
        data = csv.reader(f)
        reachable = [row for row in data]
    all_camera = []
    with open("camera.csv", "r") as f:
        data = csv.reader(f)
        for row in data:
            if [row[1]] in reachable:
                camera = models.Camera(agent_id=1, camera_id=int(row[0]), ip_address=row[1], username="admin", 
                                password="123456a@", encodeType="h265", type="rtsp", stream=False, width=3840, height=2160)
                all_camera.append(camera)
                db.add(camera)
                db.commit()
                db.refresh(camera)
    db.close()
    return all_camera

@app.post("/Create_sample_database", status_code=status.HTTP_201_CREATED)
async def create_sample_database(cam_per_instance: int, db: Session = Depends(get_db)):
    add_cam_to_instance(db, cam_per_instance)

def add_cam_to_instance(db: Session, cam_per_instance):
    try:
        db.query(models.Agent).delete()
        db.query(models.DsInstance).delete()
        db.query(models.Camera).delete()
        db.commit()
    except:
        db.rollback()    
        
    all_camera_records = add_camera_from_file(db)
    num_camera = len(all_camera_records)
    import math
    num_instance = math.ceil(num_camera / cam_per_instance)
    num_cam_left = 0
    all_instance = []
    agent = models.Agent(agent_name="x1server", ip_address="172.21.100.242")
    for i in range(num_instance):
        num_cam_left = num_camera - cam_per_instance * i
        if num_cam_left > cam_per_instance:
            num_cam_assign = cam_per_instance
        else:
            num_cam_assign = num_cam_left
        instance = models.DsInstance(instance_name="ds-" + str(i), 
                                app_type="NORMAL",
                                face_raw_meta_topic="RawFaceMeta",
                                mot_raw_meta_topic="RawMotMeta",
                                visual_topic="RawImage",
                                kafka_connection_str="172.21.100.242:9092",
                                streammux_output_width=3840,
                                streammux_output_height=2160,
                                streammux_batch_size=num_cam_assign,
                                streammux_buffer_pool=40,
                                streammux_nvbuf_memory_type=3,
                                face_confidence_threshold=0.1,
                                mot_confidence_threshold=0.3,
                                gpu_id= i % 4)
        all_instance.append(instance)
    agent.camera = all_camera_records
    agent.dsInstance = all_instance
    for i in range(num_instance):
        first = cam_per_instance * i
        last = cam_per_instance * (i + 1)
        if last > num_camera:
            last = num_camera
        all_instance[i].camera = all_camera_records[first:last]
    
    db.add(agent)
    db.commit()
    db.refresh(agent)
    for dsInstance in all_instance:
        db.add(dsInstance)
        db.commit()
        db.refresh(dsInstance)
    db.close()
    

    
    
def create_sample_database(db: Session):
    camera1 = models.Camera(camera_id=3, ip_address="172.21.111.101", username="admin", 
                            password="123456a@", encodeType="h265", type="rtsp", stream=False,width=3840, height=2160)
    camera2 = models.Camera(camera_id=1, ip_address="172.21.111.104", username="admin", 
                            password="123456a@", encodeType="h265", type="rtsp", stream=False, width=3840, height=2160)
    camera3 = models.Camera(camera_id=2, ip_address="172.21.111.111", username="admin", 
                            password="123456a@", encodeType="h265", type="rtsp", stream=False, width=3840, height=2160)
    camera4 = models.Camera(camera_id=4, ip_address="172.21.104.112", username="admin", 
                            password="123456a@", encodeType="h265", type="rtsp", stream=False, width=3840, height=2160)
    
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
                                   face_confidence_threshold=0.1,
                                   mot_confidence_threshold=0.3)
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
                                   face_confidence_threshold=0.1,
                                   mot_confidence_threshold=0.7)

    data = [camera1, camera2, camera3, camera4, agent1, agent2, dsInstance1, dsInstance2]
    agent1.camera = [camera1, camera2, camera3, camera4]
    agent1.dsInstance = [dsInstance1, dsInstance2]
    dsInstance1.camera = [camera1, camera2]
    dsInstance2.camera = [camera3, camera4]
    for cam in data:
        db.add(cam)
        db.commit()
        db.refresh(cam)
    db.close()


if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=4444)
    
    # db = Session(bind=engine)
    # add_cam_to_instance(db, 12)
    # add_camera_from_file(db)
    # create_sample_database(db)  
