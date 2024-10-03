import enum
from shared_kernel.domain.value_object import ValueObject

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
    def check(value: float, parametrized_value: float) -> bool:
        return value < parametrized_value


class GreaterThanAlarmType(AlarmTypeBase):
    @staticmethod
    def check(value: float, parametrized_value: float) -> bool:
        return value > parametrized_value
    

class DesvestAlarmType(AlarmTypeBase):
    @staticmethod
    def check(value: float, parametrized_value: float) -> bool:
        return value > parametrized_value