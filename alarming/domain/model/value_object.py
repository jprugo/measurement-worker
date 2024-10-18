import enum
from typing import List
from shared_kernel.domain.value_object import ValueObject
from measurement.domain.model.aggregate import Measure

class AlarmType(ValueObject, str, enum.Enum):
    DESVEST = "DESVEST"
    GREATER_THAN = "GREATER_THAN"
    LOWER_THAN = "LOWER_THAN"

class AlarmTypeBase():
    pass

class AlarmTypeFactory:
    @staticmethod
    def get_alarm(alarm_type: AlarmType):
        if alarm_type == AlarmType.DESVEST:
            return DesvestAlarmType()
        elif alarm_type == AlarmType.GREATER_THAN:
            return GreaterThanAlarmType()
        elif alarm_type == AlarmType.LOWER_THAN:
            return LowerThanAlarmType()
        raise ValueError("Invalid alarm type")
    

class LowerThanAlarmType(AlarmTypeBase):
    @staticmethod
    def check(parametrized_value: float, measures: List[Measure]) -> bool:
        return measures[-1] < parametrized_value


class GreaterThanAlarmType(AlarmTypeBase):
    @staticmethod
    def check(parametrized_value: float, measures: List[Measure]) -> bool:
        return measures[-1] > parametrized_value
    

class DesvestAlarmType(AlarmTypeBase):
    @staticmethod
    def check(parametrized_value: float, measures: List[Measure]) -> bool:
        last = measures[-1]
        new_list = measures[-3:-1]
        return any(x for x in new_list if abs(last - x) > parametrized_value)
