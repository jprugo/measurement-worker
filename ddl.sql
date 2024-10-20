CREATE TABLE measures (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    value REAL NOT NULL,
    measure_type TEXT NOT NULL,
    detail TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (id) -- Constraint equivalent to UniqueConstraint in SQLAlchemy
);

CREATE TABLE alarms (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    measure_value INTEGER NOT NULL,
    config_value REAL NOT NULL,
    measure_type TEXT NOT NULL,
    alarm_type TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE alarm_definitions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    config_value REAL NOT NULL,
    alarm_type TEXT NOT NULL,
    measure_type TEXT NOT NULL,
    sound_path TEXT NOT NULL,
    created_at DATETIME NOT NULL,
    updated_at DATETIME
);

CREATE TABLE configurations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    value TEXT NOT NULL,
    treatment_as TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (id) -- Constraint equivalent to UniqueConstraint in SQLAlchemy
);

CREATE TABLE step_definitions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    position TEXT NOT NULL,
    duration INTEGER NOT NULL,
    period INTEGER NOT NULL,
    lead INTEGER NOT NULL,
    sensor_type TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO configurations
(name, value, treatment_as, created_at, updated_at)
VALUES('DEVICE_IP', '192.168.1.1', 'STRING', '2024-10-11 20:04:44', '2024-10-11 20:04:44');
VALUES('isolationVoltage', '500', 'STRING', '2024-10-11 20:04:44', '2024-10-11 20:04:44');