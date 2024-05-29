from enum import Enum

class AlarmType(str, Enum):
    DESVEST = "DESVEST"
    LOWER_THAN = "LOWER_THAN"

class MeasureSensorType(str, Enum):
    RES = "RES"
    ISO = "ISO"
    WELL = "WELL"