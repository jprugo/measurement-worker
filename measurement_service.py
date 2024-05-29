import requests
from measure_sensor_type import MeasureSensorType
from constants import DEVICE_BASE_PATH, API_URL, API_ALARM_URL
from logger import logger

class DataTransformerFactory:
    """Factory class for creating data transformers."""
    @staticmethod
    def get_transformer(transformer_type):
        """Get transformer object based on type."""
        if transformer_type == MeasureSensorType.ISO:
            return IsolationDataTransformer()
        elif transformer_type == MeasureSensorType.RES:
            return ResistanceDataTransformer()
        elif transformer_type == MeasureSensorType.WELL:
            return WellDataTransformer()
        else:
            raise ValueError("Invalid transformer type")

class WellDataTransformer:
    """Transforms pressure data."""
    def transform_data(self, data):
        """Transform data to pressure format."""
        return [
            # Pressure
            {"query": f"mutation {{ addPressure(data: {{ value: {data['Presion C']}, type: \"C\" }}) {{ value }} }}"},
            {"query": f"mutation {{ addPressure(data: {{ value: {data['Presion D']}, type: \"D\" }}) {{ value }} }}"},
            # Temperature
            {"query": f"mutation {{ addTemperature(data: {{ value: {data['Temp C']}, type: \"C\" }}) {{ value }} }}"},
            {"query": f"mutation {{ addTemperature(data: {{ value: {data['Temp Motor']}, type: \"M\" }}) {{ value }} }}"},
            # Vibration
            {"query": f"mutation {{ addVibration(data: {{ value: {data['Vibracion X']}, type: \"X\" }}) {{ value }} }}"},
            {"query": f"mutation {{ addVibration(data: {{ value: {data['Vibracion Z']}, type: \"Z\" }}) {{ value }} }}"}
        ]

class IsolationDataTransformer:
    """Transforms isolation data."""
    def transform_data(self, data):
        """Transform data to isolation format."""
        return [{"query": f"mutation {{ addIsolation(data: {{ value: {data['Aislamiento']} }}) {{ value }} }}"}]

class ResistanceDataTransformer:
    """Transforms resistance data."""
    def transform_data(self, data):
        """Transform data to resistance format."""
        return [
            {"query": f"mutation {{ addResistance(data: {{ value: {data['Resistencia'][0]}, type: \"1\" }}) {{ value }} }}"},
            {"query": f"mutation {{ addResistance(data: {{ value: {data['Resistencia'][1]}, type: \"2\" }}) {{ value }} }}"},
            {"query": f"mutation {{ addResistance(data: {{ value: {data['Resistencia'][2]}, type: \"3\" }}) {{ value }} }}"}
        ]

def get_measure_data(type: str):
    """Retrieve measurement data from device."""
    try:
        url = f"{DEVICE_BASE_PATH}/{type}"
        logger.info('Making request to: '+ url)
        r = requests.get(url)
        r.raise_for_status()
        return r.json()
    except requests.RequestException as e:
        logger.error(e)
        # Handle request error here
        raise RuntimeError(f"Failed to fetch measurement data: {e}")

def upload(data):
    """Upload data to backend."""
    try:
        logger.info('Making request to: '+ API_URL)
        r = requests.post(API_URL, json=data)
        r.raise_for_status()
    except requests.RequestException as e:
        # Handle request error here
        logger.error(e)
        raise RuntimeError(f"Failed to upload data to backend: {e}")
    
def stop():
    """Send action stop voltage input"""
    try:
        url = f"{DEVICE_BASE_PATH}/stop"
        logger.info('Making request to: '+ url)
        r = requests.get(url)
        r.raise_for_status()
    except requests.RequestException as e:
        # Handle request error here
        logger.error(e)
        raise RuntimeError(f"Failed stopping voltage input: {e}")
    
def create_alarm():
    """Upload alarm to backend."""
    try:
        logger.info('Making request to: '+ API_ALARM_URL)
        r = requests.post(API_ALARM_URL)
        r.raise_for_status()
    except requests.RequestException as e:
        # Handle request error here
        logger.error(e)
        raise RuntimeError(f"Failed to upload data to backend: {e}")

def sense_measurement(transformer_type: MeasureSensorType):
    """Sense measurement data and upload transformed data."""
    logger.info('Getting data from device')
    data = get_measure_data(transformer_type.value)
    # Validate if Deteccion V is present
    if 'Deteccion V' in data:
        if data['Deteccion V'] == "true":
            logger.info("Deteccion V en body")
            create_alarm()
    transformer = DataTransformerFactory.get_transformer(transformer_type)
    transformed_data = transformer.transform_data(data)
    for transformation in transformed_data:
        logger.info('Sending data to backend')
        upload(transformation)
    return data