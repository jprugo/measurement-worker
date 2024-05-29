from fastapi import FastAPI, BackgroundTasks
from fastapi.responses import JSONResponse
from measurement_service import sense_measurement, stop
from measure_sensor_type import MeasureSensorType
import schedule
import time
import uvicorn
from fastapi_utilities import repeat_at
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
import requests
from constants import API_CONFIG_URL
from logger import logger
import threading

# APP CONFIG
logger.info(f'Making request to: {API_CONFIG_URL}')
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
        "cron": getValueFromConfigData("isolationCron"), 
        "period": getValueFromConfigData("isolationPeriod"),
        "duration": getValueFromConfigData("isolationDuration"),
        "measurement_type": MeasureSensorType.ISO, 
    },
    {
        "cron": getValueFromConfigData("resistanceCron"), 
        "period": getValueFromConfigData("resistancePeriod"),
        "duration": getValueFromConfigData("resistanceDuration"),
        "measurement_type": MeasureSensorType.RES,
    },

    # Datos sensor de pozo
    {
        "cron": getValueFromConfigData("wellCron"), 
        "period": getValueFromConfigData("wellPeriod"),
        "duration": getValueFromConfigData("wellDuration"),
        "measurement_type": MeasureSensorType.WELL, 
    },
]


class TaskScheduler:
    def __init__(self, cron: Optional[str], period: int, duration: int, measurement_type: str):
        self.cron = cron
        self.period = period
        self.duration = duration
        self.measurement_type = measurement_type

    def stop_measurement(self):
        stop_measurement(self.measurement_type)

    def start_measurement(self):

        period =  int(self.period)
        logger.info(f'{self.measurement_type} measure activated by cron with period: {period}')

        if period > 0:   
            # The first execution
            sense_measurement(self.measurement_type)
            execute_measurement(self.measurement_type)
        else:
            logger.info(f'{self.measurement_type} simple measure requested')
            return sense_measurement(self.measurement_type)


def create_task_scheduler(cron: Optional[str], period: int, duration: int, measurement_type: str) -> TaskScheduler:
    return TaskScheduler(cron, period, duration, measurement_type)

def stop_measurement(measurement_type: MeasureSensorType):
        schedule.clear(measurement_type)
        logger.info(f'Stopping {measurement_type} measurement')
        if measurement_type == MeasureSensorType.ISO:
            stop()

def execute_measurement(measurement_type: MeasureSensorType, period: int, duration):
    schedule.every(period).seconds.do(sense_measurement, measurement_type).tag(measurement_type)

    # Temporizador para finalizar los procesos
    start_time = time.time()

    while time.time() - start_time < (int(duration)*60):
        schedule.run_pending()
        time.sleep(1)

    stop_measurement(measurement_type)

@app.on_event("startup")
def start_tasks():
    logger.info('configuring task')

    loopDuration = getValueFromConfigData("loopDuration")

    if loopDuration:
        print('New flow')
        while True:
            durations = [
                int(getValueFromConfigData("durationMeasure1")),
                int(getValueFromConfigData("durationMeasure2")),
                int(getValueFromConfigData("durationMeasure3"))
            ]
            periodicities = [
                int(getValueFromConfigData("periodMeasure1")),
                int(getValueFromConfigData("periodMeasure2")),
                int(getValueFromConfigData("periodMeasure2"))
            ]
            measures = [
                MeasureSensorType[getValueFromConfigData("measure1")],
                MeasureSensorType[getValueFromConfigData("measure2")],
                MeasureSensorType[getValueFromConfigData("measure3")],
            ]
            leads = [int(getValueFromConfigData("leadTime1")), int(getValueFromConfigData("leadTime2"))]
            # Crear y lanzar los hilos para cada ejecución
            for i, (measure, periodicity, duration) in enumerate(zip(measures, periodicities ,durations)):
                    thread = threading.Thread(target=execute_measurement, args=(measure, periodicity, duration))
                    thread.start()
                    
                    if i < len(leads):
                        print(f"waiting {leads[i]} seconds before next execution...")
                        time.sleep(leads[i])
                    else:
                        print("No more lead times :D.")

                    thread.join()  # Esperar a que el hilo termine antes de continuar con el siguiente

            print("All executions done by this instance.")
    else:
        print("Old flow")
        for task_data in tasks_data:
            
            if task_data["cron"]:
                task_scheduler = create_task_scheduler(
                    cron=task_data['cron'],
                    period=task_data['period'],
                    duration=task_data['duration'],
                    measurement_type=task_data['measurement_type']
                )
                logger.info(f"task will be executed by cron:  {task_data['cron']}" )
                repeat_at(cron=task_data['cron'])(task_scheduler.start_measurement)()


@app.get("/health")
def health():
    return {"status": "200"}

@app.get("/sense")
async def sense(type: MeasureSensorType, background_tasks: BackgroundTasks):
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
