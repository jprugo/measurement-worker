import requests
from measure_type import MeasureType
from constants import DEVICE_BASE_PATH, API_URL, API_ALARM_URL

class DataTransformerFactory:
    """Factory class for creating data transformers."""
    @staticmethod
    def get_transformer(transformer_type):
        """Get transformer object based on type."""
        if transformer_type == MeasureType.TEMP:
            return TemperatureDataTransformer()
        elif transformer_type == MeasureType.ISO:
            return IsolationDataTransformer()
        elif transformer_type == MeasureType.RES:
            return ResistanceDataTransformer()
        elif transformer_type == MeasureType.PRES:
            return PressureDataTransformer()
        elif transformer_type == MeasureType.VIB:
            return VibrationDataTransformer()
        else:
            raise ValueError("Invalid transformer type")

class TemperatureDataTransformer:
    """Transforms temperature data."""
    def transform_data(self, data):
        """Transform data to temperature format."""
        return [
            {"query": f"mutation {{ addTemperature(data: {{ value: {data['Temp C']}, type: \"C\" }}) {{ value }} }}"},
            {"query": f"mutation {{ addTemperature(data: {{ value: {data['Temp Motor']}, type: \"M\" }}) {{ value }} }}"}
        ]

class PressureDataTransformer:
    """Transforms pressure data."""
    def transform_data(self, data):
        """Transform data to pressure format."""
        return [
    {"query": f"mutation {{ addPressure(data: {{ value: {data['Presion C']}, type: \"C\" }}) {{ value }} }}"},
    {"query": f"mutation {{ addPressure(data: {{ value: {data['Presion D']}, type: \"D\" }}) {{ value }} }}"}
]

    
class VibrationDataTransformer:
    """Transforms vibration data."""
    def transform_data(self, data):
        """Transform data to vibration format."""
        return [
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
            {"query": f"mutation {{ addResistance(data: {{ value: {data['Resistencia'][0]}, type: 1 }}) {{ value }} }}"},
            {"query": f"mutation {{ addResistance(data: {{ value: {data['Resistencia'][1]}, type: 2 }}) {{ value }} }}"},
            {"query": f"mutation {{ addResistance(data: {{ value: {data['Resistencia'][2]}, type: 3 }}) {{ value }} }}"}
        ]

def get_measure_data(type: str):
    """Retrieve measurement data from device."""
    try:
        url = f"{DEVICE_BASE_PATH}/{type}"
        print('Making request to: '+ url)
        r = requests.get(url)
        r.raise_for_status()
        return r.json()
    except requests.RequestException as e:
        print(e)
        # Handle request error here
        raise RuntimeError(f"Failed to fetch measurement data: {e}")

def upload(data):
    """Upload data to backend."""
    try:
        print('Making request to: '+ API_URL)
        r = requests.post(API_URL, json=data)
        r.raise_for_status()
    except requests.RequestException as e:
        # Handle request error here
        print(e)
        raise RuntimeError(f"Failed to upload data to backend: {e}")
    
def stop():
    """Send action stop voltage input"""
    try:
        url = f"{DEVICE_BASE_PATH}/stop"
        print('Making request to: '+ url)
        r = requests.get(url)
        r.raise_for_status()
    except requests.RequestException as e:
        # Handle request error here
        print(e)
        raise RuntimeError(f"Failed stopping voltage input: {e}")
    
def create_alarm():
    """Upload alarm to backend."""
    try:
        print('Making request to: '+ API_ALARM_URL)
        r = requests.post(API_ALARM_URL)
        r.raise_for_status()
    except requests.RequestException as e:
        # Handle request error here
        print(e)
        raise RuntimeError(f"Failed to upload data to backend: {e}")

def sense_measurement(transformer_type: MeasureType):
    """Sense measurement data and upload transformed data."""
    print('Getting data from device')
    data = get_measure_data(transformer_type.value)
    if data['Deteccion V'] == "true":
        create_alarm()
    transformer = DataTransformerFactory.get_transformer(transformer_type)
    transformed_data = transformer.transform_data(data)
    for transformation in transformed_data:
        print('Sending data to backend')
        upload(transformation)
    return data