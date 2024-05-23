from fastapi import FastAPI, BackgroundTasks
from fastapi.responses import JSONResponse
from measurement_service import sense_measurement, stop
from measure_type import MeasureType
import schedule
import threading
import time
import uvicorn
from fastapi_utilities import repeat_at
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
import requests
from constants import API_CONFIG_URL

# APP CONFIG
print('Making request to: '+ API_CONFIG_URL)
r = requests.get(API_CONFIG_URL)
r.raise_for_status()
config_data = r.json()

def getValueFromConfigData(key):
    return list(filter(lambda e: e['name'] == key, config_data))[0]['value']


# APP
app = FastAPI()

origins = ["*"] 

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

tasks_data = [
    {
        "cron": getValueFromConfigData("temperatureCron"), 
        "period": getValueFromConfigData("temperaturePeriod"),
        "duration": getValueFromConfigData("temperatureDuration"),
        "measurement_type": MeasureType.TEMP, 
        "enabled": getValueFromConfigData("temperatureEnabled")
    },
    {
        "cron": getValueFromConfigData("isolationCron"), 
        "period": getValueFromConfigData("isolationPeriod"),
        "duration": getValueFromConfigData("isolationDuration"),
        "measurement_type": MeasureType.ISO, 
        "enabled": getValueFromConfigData("isolationEnabled")
    },
    {
        "cron": getValueFromConfigData("resistanceCron"), 
        "period": getValueFromConfigData("resistancePeriod"),
        "duration": getValueFromConfigData("resistanceDuration"),
        "measurement_type": MeasureType.RES, 
        "enabled": getValueFromConfigData("resistanceEnabled")
    },
    {
        "cron": getValueFromConfigData("vibrationCron"), 
        "period": getValueFromConfigData("vibrationPeriod"),
        "duration": getValueFromConfigData("vibrationDuration"),
        "measurement_type": MeasureType.VIB, 
        "enabled": getValueFromConfigData("vibrationEnabled")
    },
    {
        "cron": getValueFromConfigData("pressureCron"), 
        "period": getValueFromConfigData("pressurePeriod"),
        "duration": getValueFromConfigData("pressureDuration"),
        "measurement_type": MeasureType.PRES, 
        "enabled": getValueFromConfigData("pressureEnabled")
    }
]


class TaskScheduler:
    def __init__(self, cron: Optional[str], period: int, duration: int, measurement_type: str):
        self.cron = cron
        self.period = period
        self.duration = duration
        self.measurement_type = measurement_type

    def stop_measurement(self):
        print(f'Stopping {self.measurement_type} measurement')
        stop()
        schedule.clear(self.measurement_type)

    def start_measurement(self):

        period =  int(self.period)
        print(f'{self.measurement_type} measure activated by cron' if self.cron else f'{self.measurement_type} measure request' + f' with period: {period}' )

        if period > 0:   
            # The first execution
            sense_measurement(self.measurement_type)
            schedule.every(period).seconds.do(sense_measurement, self.measurement_type).tag(self.measurement_type)

            # Temporizador para finalizar los procesos
            timer = threading.Timer( int(self.duration)*60 , self.stop_measurement)
            timer.start()

            while True:
                schedule.run_pending()
                time.sleep(1)
        else:
            print(f'{self.measurement_type} simple measure requested')
            return sense_measurement(self.measurement_type)


def create_task_scheduler(cron: Optional[str], period: int, duration: int, measurement_type: str) -> TaskScheduler:
    return TaskScheduler(cron, period, duration, measurement_type)


@app.on_event("startup")
def start_tasks():
    print('configuring task')
    for task_data in tasks_data:
        if task_data["enabled"].lower() == 'true':
            print(task_data['measurement_type'] + ' is enabled')
            task_scheduler = create_task_scheduler(
                cron=task_data['cron'],
                period=task_data['period'],
                duration=task_data['duration'],
                measurement_type=task_data['measurement_type']
            )
            # Ensure not null or empty 
            if task_data["cron"]:
                repeat_at(cron=task_data["cron"])(task_scheduler.start_measurement)()


@app.get("/health")
def health():
    return {"status": "200"}

@app.get("/sense")
async def sense(type: MeasureType, background_tasks: BackgroundTasks):
    task_data = next((x for x in tasks_data if x['measurement_type'] == type), None)
    if task_data:
        task_scheduler = create_task_scheduler(
                cron=None, period=task_data['period'], 
                duration=task_data["duration"], measurement_type=task_data['measurement_type']
        )
        background_tasks.add_task(task_scheduler.start_measurement)
        return JSONResponse(content={"message": "Measurement started."})
    else:
        return JSONResponse(status_code=404, content={"message": "Task not found."})


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
