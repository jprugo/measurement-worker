from typing import List
from enums import MeasureSensorType
from rest_template import get, post
from constants import DEVICE_BASE_PATH, API_URL, API_ALARM_URL
from logger import logger
from alarm_type import AlarmTypeFactory
from data_transformer import DataTransformerFactory
import re

def get_measure_data(type: str):
    """Retrieve measurement data from device."""
    url = f"{DEVICE_BASE_PATH}/{type}"
    return get(url)

def upload(data):
    """Upload data to backend."""
    post(API_URL, data)
    
def stop():
    """Send action stop voltage input"""
    url = f"{DEVICE_BASE_PATH}/stop"
    get(url,  isExpectingResult= False)
    
def create_alarm():
    """Upload alarm to backend."""
    post(API_ALARM_URL)

def sense_measurement(measure_sensor_type: MeasureSensorType, historial_data: List[float]):
    """Sense measurement data and upload transformed data."""
    data = get_measure_data(measure_sensor_type.value)
    if data is not None:
        transformer = DataTransformerFactory.get_transformer(measure_sensor_type) 
        transformed_data = transformer.transform_data(data)

        # Alarms
        
        for transformation in transformed_data:
            queryStr = transformation['query']
            pattern = r'value:\s*(\d+(\.\d+)?)'

            match = re.search(pattern, queryStr)
            value = match.group(1)

            AlarmTypeFactory.get_alarm(measure_sensor_type, value, historial_data).alarm()
            logger.info('Sending data to backend')
            upload(transformation)
    return data