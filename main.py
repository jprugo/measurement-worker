from fastapi import FastAPI, BackgroundTasks
from fastapi.responses import JSONResponse
from measurement_service import sense_measurement, stop
import schedule
import time
import uvicorn
from fastapi_utilities import repeat_at
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
from constants import API_CONFIG_URL
from logger import logger
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime
import asyncio
import threading
from rest_template import get
from enums import AlarmType, MeasureSensorType

# APP CONFIG
config_data = get(API_CONFIG_URL, isThrowable=True)

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
        schedule.clear(measurement_type)
        logger.info(f'----------------------- STOP: {measurement_type} -----------------------\n')
        if measurement_type == MeasureSensorType.ISO:
            stop()

def execute_measurement(measurement_type: MeasureSensorType, period: int, duration: int, historical_data: List[float]):
    logger.info(f'************************* START: {measurement_type} *************************')
    
    schedule.every(period).seconds.do(sense_measurement, measurement_type, historical_data).tag(measurement_type)

    start_time = time.time()

    while time.time() - start_time < (duration*60):
        schedule.run_pending()
        time.sleep(1)

async def start_new_flow():
    global loopDuration, durations, periodicities, measures, leads
    logger.info("start_new_flow")
    logger.info('loop duration: ' + str(loopDuration))
    logger.info('periodicities: ' + str(periodicities))
    logger.info('durations: ' + str(durations))
    logger.info('leads: ' + str(leads))
    now = datetime.now()
    scheduler.add_job(
        start_background_task,
        'interval',
        start_date=now,
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
    
async def pullConfiguration():

    global tasks_data

    global loopDuration, durations, periodicities, measures, leads

    logger.info('pulling configuration')
    
    # New Configuration
    loopDuration = getValueFromConfigData("loopDuration")
    if loopDuration:
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
        leads = [int(getValueFromConfigData("leadTime1")), int(getValueFromConfigData("leadTime2")),int(getValueFromConfigData("leadTime3"))]
    else:    
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
        {
            "cron": getValueFromConfigData("wellCron"), 
            "period": getValueFromConfigData("wellPeriod"),
            "duration": getValueFromConfigData("wellDuration"),
            "measurement_type": MeasureSensorType.WELL, 
        },
    ]

async def start_background_task(measures, periodicities ,durations, leads):
    for (measure, periodicity, duration,lead) in zip(measures, periodicities ,durations, leads):
        temp_data = [] 
        thread = threading.Thread(target=execute_measurement, args=(measure, periodicity, duration, temp_data))
    
        logger.info('Thread started')
        thread.start()
        
        thread.join()
        logger.info('Thread stopped')
        
        logger.info(f"waiting {lead} minutes before next execution...")
        await asyncio.sleep(lead*60)
        logger.info('lead time completed.')
        
        stop_measurement(measure)

    logger.info("All executions done by this instance.")
    # Clean measurements

# Events
@app.on_event("startup")
async def start_tasks():
    logger.info('start up...')
    await pullConfiguration()

@app.on_event("shutdown")
async def shutdown_event():
    scheduler.shutdown()

@app.get("/health")
def health():
    return {"status": "200"}

# Actions
@app.get("/refresh")
async def refresh():
    global config_data
    config_data = get(API_CONFIG_URL, isThrowable=True)
    await pullConfiguration()
    return {"status": "200"}

@app.get("/startMeasurementLoop")
async def sense(background_tasks: BackgroundTasks):
    background_tasks.add_task(start_new_flow)
    return JSONResponse(content={"message": "Measurement loop started."})

@app.get("/stopMeasurementLoop")
async def sense():
    if len (scheduler.get_jobs())> 0:
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
