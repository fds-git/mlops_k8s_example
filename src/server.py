"""Бэкенд инференса модели на FastAPI"""

from typing import Optional, List
import os
import pickle
import pandas as pd
import numpy as np
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sklearn.pipeline import Pipeline

app = FastAPI()

MODEL = os.getenv("MODEL", default="../models/serialized_model.sav")


def load(path: str):
    """Функция загрузки обученной модели"""
    return pickle.load(open(path, "rb"))


class Model:
    """Класс, для работы с обученной моделью"""

    pipeline: Optional[Pipeline] = None


class Passenger(BaseModel):
    """Класс, формирующий структуру данных для единичного предсказания"""

    Pclass: int
    Name: str
    Sex: str
    Age: Optional[int] = None
    SibSp: int
    Parch: int
    Ticket: str
    Fare: float
    Cabin: Optional[str] = None
    Embarked: Optional[str] = None


class PassengerList(BaseModel):
    """Класс, формирующий структуру данных для batch предсказания"""

    passengers: List[Passenger]


@app.on_event("startup")
def load_model():
    """Загрузка модели. Производится при запуске сервера"""
    Model.pipeline = load(MODEL)


@app.get("/")
def read_healthcheck():
    """Проверка доступности сервера"""
    return {"status": "Green", "version": "0.2.0"}


@app.post("/predict")
def predict(passenger_id: int, passenger: Passenger):
    """Функция предсказания одного значения
    Входные параметры:
    passenger_id: int - id пассажира
    passenger: Passenger - информация о пассажире (JSON)"""
    dataframe = pd.DataFrame([passenger.dict()])
    dataframe.fillna(value=np.nan, inplace=True, downcast=False)
    if Model.pipeline is None:
        raise HTTPException(status_code=503, detail="No model loaded")
    try:
        pred = int(Model.pipeline.predict(dataframe)[0])
    except Exception as exept:
        raise HTTPException(status_code=400, detail=str(exept))

    return {"passenger_id": passenger_id, "survived": pred}


@app.post("/predict_batch")
def predict_batch(passengers: PassengerList):
    """Функция предсказания значений для батча
    Входные параметры:
    passengers: Passenger - информация о пассажирах (JSON[LIST[JSON]])"""
    data = passengers.dict()["passengers"]
    dataframe = pd.DataFrame(data)
    dataframe.fillna(value=np.nan, inplace=True, downcast=False)
    if Model.pipeline is None:
        raise HTTPException(status_code=503, detail="No model loaded")
    try:
        pred = Model.pipeline.predict(dataframe).tolist()
    except Exception as exept:
        raise HTTPException(status_code=400, detail=str(exept))

    return {"survived": pred}
