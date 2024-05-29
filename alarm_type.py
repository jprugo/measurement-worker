from typing import List, Dict, Optional
import pygame
import numpy as np

from constants import API_ALARM_CONFIGURATION_URL
from enums import MeasureSensorType
from logger import logger
from rest_template import get
from enums import AlarmType as AlarmTypeEnum

class AlarmTypeFactory:
    @staticmethod
    def get_alarm(measure_sensor_type: MeasureSensorType, value: float, data: List):
        config = get_alarm_type_config_bd(measure_sensor_type)
        config_value = config['value']
        sound_path = config['soundPath']
        alarm_type = AlarmTypeEnum[config['alarmType']]
        if alarm_type == AlarmTypeEnum.DESVEST:
            return DesvestAlarmType(config_value, value, sound_path ,data)
        elif alarm_type == AlarmType.LOWER_THAN:
            return LowerThanAlarmType(config_value, value, sound_path, data)
        raise ValueError("Invalid alarm type")

def get_alarm_type_config_bd(measure_sensor_type: MeasureSensorType) -> Optional[Dict]:
    try:
        alarm_config = get(API_ALARM_CONFIGURATION_URL)
        logger.info(alarm_config)
        g = filter(lambda i: i['sensorType'] == measure_sensor_type.value, alarm_config)
        if g is not None:
            return next(g)
    except:
        raise Exception("No found configuration for '{measure_sensor_type.value}'")
    
class AlarmType:
    def __init__(self, config_value: float, measure_value: float, sound_path: str, historical_data: List[float]) -> None:
        self.config_value = config_value
        self.measure_value = measure_value
        logger.info(f"antes: {historical_data}")
        self.historical_data = historical_data
        self.sound_path = sound_path

    def reproduce(self):
        pygame.mixer.init()
        pygame.mixer.music.load(self.sound_path)
        pygame.mixer.music.play()
    
    def append_measure(self):
        logger.info(f"adding measure to history: {self.measure_value}")
        self.historical_data.append(int(self.measure_value))

class LowerThanAlarmType(AlarmType):
    def __init__(self, config_value: float, measure_value: float, sound_path: str, historical_data: List[float]) -> None:
        super().__init__(config_value, measure_value, sound_path, historical_data)
        self.append_measure()

    def alarm(self):
        if self.measure_value < self.config_value:
            self.reproduce()

class DesvestAlarmType(AlarmType):
    def __init__(self, config_value: float, measure_value: float, sound_path: str ,historical_data: List[float]) -> None:
        super().__init__(config_value, measure_value, sound_path, historical_data)
        self.append_measure()

    def alarm(self):
        logger.info(f"despues: {self.historical_data}")
        if self.historical_data:
            desvest = np.std(self.historical_data)
            if desvest >= self.config_value:
                self.reproduce()