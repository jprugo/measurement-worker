from fastapi import FastAPI, BackgroundTasks
from fastapi.responses import JSONResponse
from measurement_service import sense_measurement, stop
import uvicorn
from fastapi_utilities import repeat_at
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
from constants import API_CONFIG_URL
from logger import logger
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from datetime import datetime, timedelta
import asyncio
from rest_template import get
from enums import MeasureSensorType

# APP CONFI
def get_config_data():
    return get(API_CONFIG_URL, isThrowable=False)

def get_value_from_config_data(key):
    return list(filter(lambda e: e['name'] == key, config_data))[0]['value']

config_data = get_config_data()

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

scheduler = AsyncIOScheduler()

# Variables
tasks_data = []
loopDuration, durations, periodicities, measures, leads = [], [], [], [], []

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
        logger.info(f'----------------------- STOP: {measurement_type} -----------------------\n')
        if measurement_type == MeasureSensorType.ISO:
            stop()

def stop_scheduler_after_duration(duration: int, measurement_type: MeasureSensorType):
    def shutdown(measurement_type: MeasureSensorType):
        scheduler.remove_job(measurement_type)
    
    scheduler.add_job(shutdown, 'date', run_date=datetime.now() + timedelta(minutes=duration), args=[measurement_type])


async def execute_measurement(measurement_type: MeasureSensorType, period: int, duration: int, historical_data: List[float]):
    logger.info(f'************************* START: {measurement_type} *************************')
    scheduler.add_job(
        sense_measurement,
        IntervalTrigger(seconds=period),
        start_date=datetime.now() + timedelta(seconds=1),
        args=(measurement_type, historical_data),
        id=measurement_type,
        replace_existing=True
    )
    stop_scheduler_after_duration(duration, measurement_type)
    await asyncio.sleep(duration*60)


async def start_new_flow():
    global loopDuration, durations, periodicities, measures, leads
    logger.info("start_new_flow")
    logger.info('loop duration: ' + str(loopDuration))
    logger.info('periodicities: ' + str(periodicities))
    logger.info('durations: ' + str(durations))
    logger.info('leads: ' + str(leads))
    scheduler.add_job(
        start_background_task,
        'interval',
        start_date= datetime.now() + timedelta(seconds=1),
        args=(measures, periodicities, durations, leads),
        minutes=int(loopDuration),
        id='start_background_task',
        replace_existing=True
    )
    scheduler.start()

async def start_old_flow():
    logger.info("start_old_flow")
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
    
async def pull_configuration():

    global tasks_data

    global loopDuration, durations, periodicities, measures, leads

    logger.info('pulling configuration')
    
    # New Configuration
    loopDuration = get_value_from_config_data("loopDuration")
    if loopDuration:
        durations = [
                int(get_value_from_config_data("durationMeasure1")),
                int(get_value_from_config_data("durationMeasure2")),
                int(get_value_from_config_data("durationMeasure3"))
            ]
        periodicities = [
            int(get_value_from_config_data("periodMeasure1")),
            int(get_value_from_config_data("periodMeasure2")),
            int(get_value_from_config_data("periodMeasure2"))
        ]
        measures = [
            MeasureSensorType[get_value_from_config_data("measure1")],
            MeasureSensorType[get_value_from_config_data("measure2")],
            MeasureSensorType[get_value_from_config_data("measure3")],
        ]
        leads = [int(get_value_from_config_data("leadTime1")), int(get_value_from_config_data("leadTime2")),int(get_value_from_config_data("leadTime3"))]
    else:    
        tasks_data = [
        {
            "cron": get_value_from_config_data("isolationCron"), 
            "period": get_value_from_config_data("isolationPeriod"),
            "duration": get_value_from_config_data("isolationDuration"),
            "measurement_type": MeasureSensorType.ISO, 
        },
        {
            "cron": get_value_from_config_data("resistanceCron"), 
            "period": get_value_from_config_data("resistancePeriod"),
            "duration": get_value_from_config_data("resistanceDuration"),
            "measurement_type": MeasureSensorType.RES,
        },
        {
            "cron": get_value_from_config_data("wellCron"), 
            "period": get_value_from_config_data("wellPeriod"),
            "duration": get_value_from_config_data("wellDuration"),
            "measurement_type": MeasureSensorType.WELL, 
        },
    ]

async def start_background_task(measures, periodicities ,durations, leads):
    for (measure, periodicity, duration,lead) in zip(measures, periodicities ,durations, leads):
        temp_data = []
        
        await execute_measurement(measure, periodicity, duration, temp_data)
 
        logger.info(f"waiting {lead} minutes before next execution...")
        stop_measurement(measure)
        await asyncio.sleep(lead*60)
        logger.info('lead time completed.')

    logger.info("All executions done by this instance.")
    # Clean measurements

# Events
@app.on_event("startup")
async def start_tasks():
    logger.info('start up...')
    await pull_configuration()

@app.on_event("shutdown")
async def shutdown_event():
    scheduler.remove_all_jobs()
    scheduler.shutdown()

@app.get("/health")
def health():
    return {"status": "200"}

# Actions
@app.get("/refresh")
async def refresh():
    global config_data
    config_data = get_config_data()
    await pull_configuration()
    return {"status": "200"}

@app.get("/startMeasurementLoop")
async def start_measurement_loop(background_tasks: BackgroundTasks):
    background_tasks.add_task(start_new_flow)
    return JSONResponse(content={"message": "Measurement loop started."})

@app.get("/stopMeasurementLoop")
async def stopMeasurementLoop():
    if len (scheduler.get_jobs())> 0:
        scheduler.remove_all_jobs()
        scheduler.shutdown()
        return JSONResponse(content={"message": "Measurement loop stopped."})
    else: 
        return JSONResponse(content={"message": "No measurement loop in exectution."}, status_code=204)

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

# Main
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
