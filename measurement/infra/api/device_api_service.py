import requests

from configuration.application.use_case import ConfigurationQueryUseCase, GetConfigurationRequest
from measurement.domain.model.value_object import SensorType, MeasureDeviceResponse

class DeviceApiService:

    def __init__(self, config_query: ConfigurationQueryUseCase) -> None:
        self.base_url = config_query.get_configuration(
            GetConfigurationRequest(
                name = "DEVICE_IP"
            )
        )[0].value


    def fetch_data(self, sensor_type: SensorType) -> MeasureDeviceResponse:
        full_path = f"{self.base_url}/{sensor_type}"
        print(f'Making request to: {full_path}')
        response = requests.get(full_path)
        print(f'Response: {response.status_code}')
        return MeasureDeviceResponse(**response.json())
        

    def stop(self) -> None:
        full_path = f"{self.base_url}/stop"
        print(f'Making request to: {full_path}')
        response = requests.get(full_path)
        print(f'Response: {response.status_code}')