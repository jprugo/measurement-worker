

from enums import MeasureSensorType


class DataTransformerFactory:
    """Factory class for creating data transformers."""
    @staticmethod
    def get_transformer(measure_sensor_type: MeasureSensorType):
        """Get transformer object based on type."""
        if measure_sensor_type == MeasureSensorType.ISO:
            return IsolationDataTransformer()
        elif measure_sensor_type == MeasureSensorType.RES:
            return ResistanceDataTransformer()
        elif measure_sensor_type == MeasureSensorType.WELL:
            return WellDataTransformer()

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