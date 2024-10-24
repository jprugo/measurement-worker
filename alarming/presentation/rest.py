from typing import List

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends

from alarming.presentation.response import AlarmResponse, AlarmDefinitionResponse, AlarmSchema, AlarmDefinitionSchema
from alarming.application.use_case import (
    AlarmDefinitionQueryUseCase, AlarmQueryUseCase, 
    CreateAlarmCommand, CreateAlarmDefinitionCommand, UpdateAlarmDefinitionCommand, 
    RegisterAlarmDefinitionRequest, RegisterAlarmRequest, UpdateAlarmDefinitionRequest
)

from alarming.domain.model.aggregate import Alarm, AlarmDefinition
from shared_kernel.infra.container import AppContainer

router = APIRouter(
    #prefix="/alarming", tags=['alarming']
)

###############################################################
#                      ALARM DEFINITION                       #
###############################################################

@router.get("/alarmDefinition", tags=['alarmDefinition'])
@inject
def get_alarms_definition(
    query: AlarmDefinitionQueryUseCase = Depends(Provide[AppContainer.alarm.alarm_definition_query]),
) -> AlarmDefinitionResponse:
    alarms_definitions: List[AlarmDefinition] = query.get_alarms_definition()
    return AlarmDefinitionResponse(
        detail="ok",
        result=[AlarmDefinitionSchema.from_orm(ad) for ad in alarms_definitions]
    )

@router.post("/alarmDefinition", tags=['alarmDefinition'])
@inject
def post_alarm_definition(
    request: RegisterAlarmDefinitionRequest = Depends(),
    command: CreateAlarmDefinitionCommand = Depends(Provide[AppContainer.alarm.create_alarm_definition_command])
) -> None:
    command.execute(request=request)


@router.put("/alarmDefinition", tags=['alarmDefinition'])
@inject
def update_alarm_definition(
    request: UpdateAlarmDefinitionRequest = Depends(),
    command: UpdateAlarmDefinitionCommand = Depends(Provide[AppContainer.alarm.update_alarm_definition_command])
) -> None:
    command.execute(request=request)

###############################################################
#                           ALARM                             #
###############################################################


# TODO: (ruedag.jp@gmail.com) Add feature to filter by date range
@router.get("/alarm", tags=['alarm'])
@inject
def get_alarms(
    query: AlarmQueryUseCase = Depends(Provide[AppContainer.alarm.alarm_query]),
) -> AlarmResponse:
    alarms: List[Alarm] = query.get_alarms()
    return AlarmResponse(
        detail="ok",
        result=[AlarmSchema.from_orm(a) for a in alarms]
    )


@router.post("/alarm", tags=['alarm'])
@inject
def post_alarm(
    request: RegisterAlarmRequest= Depends(),
    command: CreateAlarmCommand = Depends(Provide[AppContainer.alarm.create_alarm_command])
) -> None:
    command.execute(request=request)