from typing import List, Optional
from datetime import datetime

from pydantic import BaseModel

from measurement.domain.model.value_object import MeasureType
from shared_kernel.presentation.response import BaseResponse


class MeasurementSchema(BaseModel):
    id: int
    value: float
    created_at: datetime
    measure_type: MeasureType
    detail: Optional[str] = None

    class Config:
        orm_mode = True
        from_attributes=True
        json_encoders = {
            datetime: lambda v: v.isoformat()  # Convierte a ISO 8601
        }


class MeasurementResponse(BaseResponse):
    result: List[MeasurementSchema] = None