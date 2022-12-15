from fastapi import FastAPI, status, HTTPException
from database import Base, engine
from sqlalchemy.orm import Session
from models import Agent
from schema import AgentInfo, AgentCreate

Base.metadata.create_all(engine)

app = FastAPI()


@app.get("/")
def root():
    return "CRUD agent information"


@app.post("/coordinator", status_code=status.HTTP_201_CREATED)
def create_coordinator(agentInfo: AgentCreate):
    session = Session(bind=engine, expire_on_commit=False)
    new_info = Agent(computer_id = agentInfo.computer_id, ip_address=agentInfo.ip_address)
    session.add(new_info)
    session.commit()
    session.refresh(new_info)
    
    session.close()
    
    return new_info


@app.get("/coordinator/{id}")
def read_coordinator(id: int):
    session = Session(bind=engine, expire_on_commit=False)
    agent = session.query(Agent).get(id)
    session.close()
    
    if not agent:
        raise HTTPException(status_code=404, detail=f"Agent item with id {id} not found")
    return agent

@app.put("/coordinator/{id}")
def update_coordinator(id: int, info: AgentInfo):
    session = Session(bind=engine, expire_on_commit=False)
    agent = session.query(Agent).get(id)
    
    if agent:
        agent.computer_id = info.computer_id
        agent.ip_address = info.ip_address
        session.commit()
    session.close()
    
    if not agent:
        raise HTTPException(status_code=404, detail=f"agent item with id {id} not found")
    
        
    return agent


@app.delete("/coordinator/{id}")
def delete_coordinator(id: int):
    session = Session(bind=engine, expire_on_commit=False)
    agent = session.query(Agent).get(id)
    
    if agent:
        session.delete(agent)
        session.commit()
        session.close()
    else:
        raise HTTPException(status_code=404, detail=f"agent item with id {id} not found")
    return None


@app.get("/coordinator")
def read_coordinator_list():
    session = Session(bind=engine, expire_on_commit=False)
    
    agent_list = session.query(Agent).all()
    
    session.close()
    return agent_list
