import models
import schema
from database import Base, SessionLocal, engine
from fastapi import Depends, FastAPI, status
from pydantic.typing import List
from sqlalchemy.orm import Session, joinedload

Base.metadata.create_all(engine)
app = FastAPI(title="Camera")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

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
                      type=cameraInfo.type)
    db.add(new_camera)
    db.commit()
    db.refresh(new_camera)
    db.close()
    
    return new_camera

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
                             hostname=agentInfo.hostname)
    db.add(new_agent)
    db.commit()
    db.refresh(new_agent)
    db.close()
    
    return new_agent

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

def create_sample_database(db: Session):
    camera1 = models.Camera(camera_id=3, ip_address="172.21.111.101", username="admin", 
                            password="123456a@", encodeType="h265", type="rtsp")
    camera2 = models.Camera(camera_id=1, ip_address="172.21.111.104", username="admin", 
                            password="123456a@", encodeType="h265", type="rtsp")
    camera3 = models.Camera(camera_id=2, ip_address="172.21.111.111", username="admin", 
                            password="123456a@", encodeType="h265", type="rtsp")
    camera4 = models.Camera(camera_id=4, ip_address="172.21.104.112", username="admin", 
                            password="123456a@", encodeType="h265", type="rtsp")
    
    data = [camera1, camera2, camera3, camera4]
    for cam in data:
        db.add(cam)
        db.commit()
        db.refresh(cam)
    db.close()


if __name__ == '__main__':
    db = Session(bind=engine)
    # create_sample_database(db)    
    q = db.query(models.Camera).where(models.Camera.ip_address == "172.21.111.111").one()
    print(q.camera_id)
    # from sqlalchemy import distinct, func

    # print(db.query(func.count(distinct(models.Camera.ip_address))))

