from typing import List, Dict, Optional
import pygame
import numpy as np

from constants import API_ALARM_CONFIGURATION_URL
from enums import MeasureSensorType
from logger import logger
from rest_template import get, post
from enums import AlarmType as AlarmTypeEnum

class AlarmTypeFactory:
    @staticmethod
    def get_alarm(measure_sensor_type: MeasureSensorType, value: float, data: List):
        config = get_alarm_type_config_bd(measure_sensor_type)
        config_value = config['value']
        sound_path = config['soundPath']
        alarm_type = AlarmTypeEnum[config['alarmType']]
        if alarm_type == AlarmTypeEnum.DESVEST:
            return DesvestAlarmType(config_value, value, sound_path, measure_sensor_type ,data)
        elif alarm_type == AlarmTypeEnum.LOWER_THAN:
            return LowerThanAlarmType(config_value, value, sound_path, measure_sensor_type ,data)
        raise ValueError("Invalid alarm type")

def get_alarm_type_config_bd(measure_sensor_type: MeasureSensorType) -> Optional[Dict]:
    try:
        alarm_config = get(API_ALARM_CONFIGURATION_URL)
        g = filter(lambda i: i['sensorType'] == measure_sensor_type.value, alarm_config)
        if g is not None:
            return next(g)
    except:
        raise Exception("No found configuration for '{measure_sensor_type.value}'")
    
class AlarmType:
    def __init__(
            self,
            config_value: float, measure_value: float,
            sound_path: str,
            sensorType: MeasureSensorType,
            # State
            historical_data: List[float]
        ) -> None:
        self.config_value = config_value
        self.measure_value = measure_value
        self.historical_data = historical_data
        self.sound_path = sound_path
        self.sensorType = sensorType

    def reproduce(self):
        pygame.mixer.init()
        pygame.mixer.music.load(self.sound_path)
        pygame.mixer.music.play()
    
    def append_measure(self):
        self.historical_data.append(float(self.measure_value))

class LowerThanAlarmType(AlarmType):
    def __init__(
            self,
            config_value: float, measure_value: float,
            sound_path: str,
            sensorType: MeasureSensorType,
            # state
            historical_data: List[float]
        ) -> None:
        super().__init__(config_value, measure_value, sound_path, sensorType ,historical_data)
        self.append_measure()

    def alarm(self):
        if float(self.measure_value) < self.config_value:
            self.reproduce()
            saveAlarmRecord(self.sensorType, AlarmTypeEnum.LOWER_THAN, self.measure_value)

class DesvestAlarmType(AlarmType):
    def __init__(
            self, 
            config_value: float, measure_value: float,
            sound_path: str,
            sensorType: MeasureSensorType,
            # State
            historical_data: List[float]
        ) -> None:
        super().__init__(config_value, measure_value, sound_path, sensorType ,historical_data)
        self.append_measure()

    def alarm(self):
        if self.historical_data:
            desvest = np.std(self.historical_data)
            if desvest >= self.config_value:
                self.reproduce()
                saveAlarmRecord(self.sensorType, AlarmTypeEnum.DESVEST, self.measure_value)

def saveAlarmRecord(
        sensorType: MeasureSensorType,
        alarmType: AlarmTypeEnum,
        value: float
    ):
    post('http://localhost:8000/alarm', {
            'sensorType': sensorType,
            'value': value,
            'alarmType': alarmType,
            'timestamp': None
        }
    )