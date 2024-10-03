from typing import  List
import asyncio

from measurement.infra.api.device_api_service import DeviceApiService
from worker.application.step_definition_use_case import StepDefinitionQueryUseCase
from worker.domain.model.aggregate import StepDefinition
from worker.domain.model.value_object import PositionType

from measurement.domain.model.value_object import DeviceMeasure, SensorType
from measurement.application.use_case import CreateMeasurementCommand, DeviceMeasurementQueryUseCase, CreateMeasurementRequest

from alarming.application.use_case import AlarmDefinitionQueryUseCase, CreateAlarmCommand
from alarming.domain.model.aggregate import AlarmDefinition
from alarming.domain.model.value_object import AlarmTypeFactory
from alarming.domain.model.services import RegisterAlarmRequest

import pygame

from shared_kernel.infra.event_manager import EventManager

class WorkerService:
    
    def __init__(
        self, 
        # WORKER
        step_definition_query: StepDefinitionQueryUseCase,
        # MEASUREMENT
        measurement_command: CreateMeasurementCommand,
        measurement_query: DeviceMeasurementQueryUseCase,
        device_api_service: DeviceApiService, 
        # ALARM
        alarm_def_query: AlarmDefinitionQueryUseCase,
        alarm_command: CreateAlarmCommand
    ):
        self.step_definition_query = step_definition_query
        # MEASUREMENT
        self.measurement_command = measurement_command
        self.measurement_query = measurement_query

        # DEVICE
        self.device_api_service = device_api_service

        # ALARM
        self.alarm_query = alarm_def_query
        self.alarm_command = alarm_command

    async def handle(self, event_manager: EventManager, position: PositionType):
        print(f"Handling position: {position}")
        data = self.step_definition_query.find_by_position(position=position)
        if data:
            step = data[0]
            duration = step.duration 
            period = step.period
            
            end_time = asyncio.get_event_loop().time() + duration * 60

            while event_manager.running:
                measures = self._get_measure(step)

                print('Saving measure and verifying alarm level')
                for measure in measures:
                    self._register_measure(measure)
                    self._verify_alarm_level(measure)

                current_time = asyncio.get_event_loop().time()
                if current_time >= end_time:
                    print('Duration completed')
                    break
                await asyncio.sleep(period)

            if event_manager.running:
                print(f'Leading time: {step.lead * 60} seconds')
                await asyncio.sleep(step.lead * 60)

            # Stop the measure only if is ISO
            if step.sensor_type == SensorType.ISO:
                self.stop_measure()

            # Get the next position
            next_position = self._get_next_position(position)
        else:
            print('Data not found for the given position. Returning the first')
            next_position = PositionType.FIRST

        event_manager.publish(next_position.value, position=next_position, event_manager=event_manager)


    def _get_measure(self, step: StepDefinition) -> List[DeviceMeasure]:
        print(f"Getting {step.sensor_type} measure from device")
        return self.measurement_query.get_measures(step.sensor_type)
    

    def stop_measure(self) -> List[DeviceMeasure]:
        print(f"Sending stop message...")
        return self.device_api_service.stop()


    def _register_measure(self, measure: DeviceMeasure):
        self.measurement_command.execute(
            CreateMeasurementRequest(
                value=measure.value,
                measure_type=measure.measure_type,
                detail= measure.detail
            )
        )


    def _verify_alarm_level(self, measure: DeviceMeasure):
        alarm_definitions = self.alarm_query.get_alarms_definition_by_measure_type(measure_type=measure.measure_type)
        if alarm_definitions:
            alarm_definition = alarm_definitions[0]
            alarm_type = AlarmTypeFactory.get_alarm(alarm_type=alarm_definition.alarm_type)
            if alarm_type.check(value=measure.value, parametrized_value=alarm_definition.config_value):
                self._trigger_alarm(alarm_definition=alarm_definition, measure_value= measure.value)


    def _get_next_position(self, current_enum: PositionType) -> PositionType:
        enum_members = list(PositionType)
        current_index = enum_members.index(current_enum)
        next_index = (current_index + 1) % len(enum_members)
        return enum_members[next_index]
    

    def _reproduce(self, sound_path: str):
        pygame.mixer.init()
        pygame.mixer.music.load(sound_path)
        pygame.mixer.music.play()


    def _save_alarm(self, alarm_definition: AlarmDefinition, measure_value: float):
        self.alarm_command.execute(
            request=RegisterAlarmRequest(
                alarm_type= alarm_definition.alarm_type,
                value= measure_value,
                config_value= alarm_definition.config_value,
                measure_type= alarm_definition.measure_type
            )
        )


    def _trigger_alarm(self, alarm_definition: AlarmDefinition, measure_value: float):
        self._reproduce(sound_path= alarm_definition.sound_path)
        self._save_alarm(alarm_definition=alarm_definition, measure_value=measure_value)
        