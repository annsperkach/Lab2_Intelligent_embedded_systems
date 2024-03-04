from typing import Any
from fastapi import HTTPException
from sqlalchemy.orm import Session
from model.models import *
from sqlalchemy import select, Row


def get_data_by_id(db: Session, processed_agent_data_id: int) -> Row[tuple[Any]] | None:
    query = select(processed_agent_data).where(processed_agent_data.c.id == processed_agent_data_id)
    result = db.execute(query)
    data = result.fetchone()
    return data


def update_data(db: Session, processed_agent_data_id: int, data: ProcessedAgentData) -> ProcessedAgentDataInDB:
    try:
        # Get the data to update from the database
        result = db.execute(select(processed_agent_data).where(processed_agent_data.c.id == processed_agent_data_id))
        existing_data = result.fetchone()

        if not existing_data:
            raise HTTPException(status_code=404, detail="Data not found")

        updateData = {
            "road_state": data.road_state,
            "x": data.agent_data.accelerometer.x,
            "y": data.agent_data.accelerometer.y,
            "z": data.agent_data.accelerometer.z,
            "latitude": data.agent_data.gps.latitude,
            "longitude": data.agent_data.gps.longitude,
            "timestamp": data.agent_data.timestamp
        }

        update_statement = (
            processed_agent_data.update()
            .where(processed_agent_data.c.id == processed_agent_data_id)
            .values(**updateData)
        )
        db.execute(update_statement)
        db.commit()

        # Update string values
        return ProcessedAgentDataInDB(
            id=processed_agent_data_id,
            road_state=updateData["road_state"],
            x=updateData["x"],
            y=updateData["y"],
            z=updateData["z"],
            latitude=updateData["latitude"],
            longitude=updateData["longitude"],
            timestamp=updateData["timestamp"]
        )

    except Exception:
        raise HTTPException(status_code=500, detail="Data updating goes wrong")


def delete_data(db: Session, processed_agent_data_id: int) -> ProcessedAgentDataInDB:
    try:
        # Delete by id
        result = db.execute(
            select(processed_agent_data).where(processed_agent_data.c.id == processed_agent_data_id))
        data_to_delete = result.fetchone()

        if not data_to_delete:
            raise HTTPException(status_code=404, detail="Data not found")

        # Creating a request to the database to delete a row by its Id
        db.execute(processed_agent_data.delete().where(processed_agent_data.c.id == processed_agent_data_id))
        db.commit()

        return ProcessedAgentDataInDB(
            id=data_to_delete[0],
            road_state=data_to_delete[1],
            x=data_to_delete[2],
            y=data_to_delete[3],
            z=data_to_delete[4],
            latitude=data_to_delete[5],
            longitude=data_to_delete[6],
            timestamp=data_to_delete[7]
        )
    except Exception:
        raise HTTPException(status_code=500, detail="Data deleting is incorrect")
