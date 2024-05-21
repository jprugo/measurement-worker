from enum import Enum

class MeasureType(str, Enum):
    TEMP = "TEMP"
    ISO = "ISO"
    RES = "RES"
    VIB = "VIB"
    PRES = "PRES"