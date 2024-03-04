from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker, Session
from starlette.websockets import WebSocket, WebSocketDisconnect
import json
from typing import Set
from fastapi import FastAPI, HTTPException, Depends

from utils import processedAgentDataQueries
from utils.constants import DATABASE_URL
from model.models import *

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
metadata = MetaData()

app = FastAPI()
subscriptions: Set[WebSocket] = set()


@app.websocket("/ws/")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    subscriptions.add(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        subscriptions.remove(websocket)


async def send_data_to_subscribers(user_id: int, data):
    if user_id in subscriptions:
        for websocket in subscriptions[user_id]:
            await websocket.send_json(json.dumps(data))


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# CRUD endpoints
@app.get("/processed_agent_data/{processed_agent_data_id}", response_model=ProcessedAgentDataInDB)
def read_processed_agent_data(processed_agent_data_id: int, db: Session = Depends(get_db)):
    try:
        data = processedAgentDataQueries.get_data_by_id(db, processed_agent_data_id)

        if not data:
            raise HTTPException(status_code=404, detail="Data not found")

        processed_data = ProcessedAgentDataInDB(
            id=data[0],
            road_state=data[1],
            user_id=data[2],
            x=data[3],
            y=data[4],
            z=data[5],
            latitude=data[6],
            longitude=data[7],
            timestamp=data[8]
        )
        return processed_data

    except Exception:
        raise HTTPException(status_code=500, detail="Data read incorrectly")


@app.post("/processed_agent_data/")
def create_processed_agent_data(data: ProcessedAgentData, db: Session = Depends(get_db)):
    try:
        road_state = data.road_state
        accelerometer = data.agent_data.accelerometer
        gps = data.agent_data.gps
        timestamp = data.agent_data.timestamp

        db.execute(processed_agent_data.insert().values(
            road_state=road_state,
            x=accelerometer.x,
            y=accelerometer.y,
            z=accelerometer.z,
            latitude=gps.latitude,
            longitude=gps.longitude,
            timestamp=timestamp
        ))
        db.commit()
        return {"message": "Data created successfully"}

    except Exception:
        raise HTTPException(status_code=500, detail="Data created wrong")


@app.get("/processed_agent_data/",
         response_model=list[ProcessedAgentDataInDB])
def list_processed_agent_data(db: Session = Depends(get_db)):
    try:
        # Create a ProcessedAgentDataInDB object from each row and add it to the list
        processed_agent_data_ = db.query(processed_agent_data).all()
        return processed_agent_data_
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/processed_agent_data/{processed_agent_data_id}", response_model=ProcessedAgentDataInDB)
def update_processed_agent_data(processed_agent_data_id: int, data: ProcessedAgentData, db: Session = Depends(get_db)):
    try:
        updated_data = processedAgentDataQueries.update_data(db, processed_agent_data_id, data)
        return updated_data

    except HTTPException as e:
        raise e


@app.delete("/processed_agent_data/{processed_agent_data_id}", response_model=ProcessedAgentDataInDB)
def delete_processed_agent_data(processed_agent_data_id: int, db: Session = Depends(get_db)):
    try:
        deleted_data = processedAgentDataQueries.delete_data(db, processed_agent_data_id)
        return deleted_data

    except HTTPException as e:
        raise e
