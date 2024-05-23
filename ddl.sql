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
(name, value, treatment_as)
VALUES('DEVICE_IP', 'https://eb53b229-f0e4-42da-9957-a7df9990fe9c.mock.pstmn.io', 'STRING');
VALUES('isolationVoltage', '500', 'STRING');

INSERT INTO step_definitions (position,duration,period,lead, sensor_type)
values 
('FIRST',1,25,1,'RES'),
('SECOND',1,25,1,'ISO'),
('THIRD',1,25,1,'WELL');