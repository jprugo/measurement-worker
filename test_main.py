import pytest
from unittest.mock import patch, Mock
from fastapi.testclient import TestClient
from main import app, pull_configuration, start_background_task
from data_transformer import MeasureSensorType

client = TestClient(app)

@pytest.fixture
def mock_get_value_from_config_data():
    with patch('main.get_config_data') as mock:
        yield mock

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "200"}

def test_refresh(mock_get_value_from_config_data):
    mock_get_value_from_config_data.return_value= mock_response
    response =  client.get("/refresh")
    assert response.status_code == 200
    assert response.json() == {"status": "200"}

mock_response = [
    {
        "name": "loopDuration",
        "value": "6"
    },
    {
        "name": "durationMeasure1",
        "value": "1"
    },
    {
        "name": "durationMeasure2",
        "value": "1"
    },
    {
        "name": "durationMeasure3",
        "value": "1"
    },
    {
        "name": "periodMeasure1",
        "value": "30"
    },
    {
        "name": "periodMeasure2",
        "value": "30"
    },
    {
        "name": "periodMeasure3",
        "value": "30"
    },
    {
        "name": "measure1",
        "value": "ISO"
    },
    {
        "name": "measure2",
        "value": "ISO"
    },
    {
        "name": "measure3",
        "value": "ISO"
    },
    {
        "name": "leadTime1",
        "value": "1"
    },
    {
        "name": "leadTime2",
        "value": "1"
    },
    {
        "name": "leadTime3",
        "value": "1"
    },        
]
@pytest.mark.asyncio
async def test_pull_configuration(mock_get_value_from_config_data):
    mock_get_value_from_config_data.return_value= mock_response
    await pull_configuration()

@pytest.mark.asyncio
async def test_start_background_task(mock_get_value_from_config_data):
    mock_get_value_from_config_data.return_value= mock_response
    durations = [0.1,0.1,0]
    periodicities = [1,1,1]
    measures = [MeasureSensorType.ISO, MeasureSensorType.RES, MeasureSensorType.ISO]
    leads = [0.1,0,0]

    requests_mock_response_success = Mock()
    requests_mock_response_success.json.return_value = [
        {
            "id": 1,
            "value": 4000,
            "sensorType": "ISO",
            "enabled": True,
            "alarmType": "LOWER_THAN",
            "soundPath": "/Users/jp/Repositories/Gwat/measurement-worker/test.wav"
        },
        {
            "id": 2,
            "value": 5,
            "sensorType": "RES",
            "enabled": True,
            "alarmType": "DESVEST",
            "soundPath": "/Users/jp/Repositories/Gwat/measurement-worker/test.wav"
        }
    ]
    with patch('measurement_service.get_measure_data', return_value={"Aislamiento": 122, 'Resistencia': [1,2,3]}), \
         patch('rest_template.requests.get', return_value=requests_mock_response_success):
            await start_background_task(measures, periodicities, durations, leads)

     
# We don't use the sense method by itself    

def test_sense_not_found():
    response =  client.get("/sense", params={"type": "ISO"})
    assert response.status_code == 404
    assert response.json() == {"message": "Task not found."}