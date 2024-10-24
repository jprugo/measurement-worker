from sqlalchemy import Column, DateTime, Text, Integer, Float, MetaData, String, Table, UniqueConstraint
from sqlalchemy.orm import registry, composite

from alarming.domain.model.value_object import AlarmType
from configuration.domain.model.value_object import TreatmentAs
from alarming.domain.model.aggregate import Alarm, AlarmDefinition
from measurement.domain.model.aggregate import Measure
from measurement.domain.model.value_object import SensorType, MeasureType
from configuration.domain.model.aggregate import Configuration
from worker.domain.model.aggregate import StepDefinition

metadata = MetaData()
mapper_registry = registry()

measures_table = Table(
    "measures",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("value", Float, nullable=False),
    Column("measure_type", String, nullable=False),
    Column("detail", String, nullable=False),
    Column("created_at", DateTime, nullable=True),
    UniqueConstraint("id", name="uix_measure_number"),
)

alarms_table = Table(
    "alarms",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("measure_value", Integer, nullable=False),
    Column("config_value", Float, nullable=False),
    Column("measure_type", String, nullable=False),
    Column("alarm_type", String, nullable=False),
    Column("created_at", DateTime, nullable=True),
)

alarms_definition_table = Table(
    "alarm_definitions",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("config_value", Float, nullable=False),
    Column("alarm_type", String, nullable=False),
    Column("measure_type", String, nullable=False),
    Column("sound_path", String, nullable=False),
    Column("created_at", DateTime, nullable=False),
    Column("updated_at", DateTime, nullable=True),
)

configuration_table = Table(
    "configurations",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("name", Text, nullable=False),
    Column("value", String, nullable=False),
    Column("treatment_as", String, nullable=False),
    UniqueConstraint("id", name="uix_config_number"),
)

step_definition_table = Table(
    "step_definitions",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("position", String, nullable=False),
    Column("duration", Integer, nullable=False),
    Column("period", Integer, nullable=False),
    Column("lead", Integer, nullable=False),
    Column("sensor_type", String, nullable=False),
    Column("created_at", DateTime, nullable=True),
    Column("updated_at", DateTime, nullable=True),
)

def init_orm_mappers():
    """
    Initialize ORM mappings.
    """

    mapper_registry.map_imperatively(
        Measure,
        measures_table,
        properties={
            "measure_type_value": composite(MeasureType.from_value, measures_table.c.measure_type),
        }
    )

    mapper_registry.map_imperatively(
        Alarm,
        alarms_table,
        properties={
            "measure_type_value": composite(MeasureType.from_value, alarms_table.c.measure_type),
            "alarm_type_value": composite(AlarmType.from_value, alarms_table.c.alarm_type),
        }
    )

    mapper_registry.map_imperatively(
        AlarmDefinition,
        alarms_definition_table,
        properties={
            "measure_type_value": composite(MeasureType.from_value, alarms_definition_table.c.measure_type),
            "alarm_type_value": composite(AlarmType.from_value, alarms_definition_table.c.alarm_type),
        }
    )

    mapper_registry.map_imperatively(
        Configuration,
        configuration_table,
        properties={
            "treatment_as_value": composite(TreatmentAs.from_value, configuration_table.c.treatment_as),
        }
    )

    mapper_registry.map_imperatively(
        StepDefinition,
        step_definition_table,
        properties={
            "sensor_type_value": composite(SensorType.from_value, step_definition_table.c.sensor_type),
        }
    )
