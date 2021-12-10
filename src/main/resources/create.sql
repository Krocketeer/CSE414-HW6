CREATE TABLE Caregivers (
    Username varchar(255),
    Salt BINARY(16),
    Hash BINARY(16),
    PRIMARY KEY (Username)
);

CREATE TABLE Availabilities (
    Time date,
    Username varchar(255) REFERENCES Caregivers(Username),
    Available int,
    PRIMARY KEY (Time, Username)
);

CREATE TABLE Vaccines (
    Name varchar(255),
    Doses int,
    PRIMARY KEY (Name)
);

CREATE TABLE Patient (
    Username varchar(255),
    Salt BINARY(16),
    Hash BINARY(16),
    PRIMARY KEY (Username)
);

CREATE TABLE Appointment (
    ID INTEGER,
    Time date,
    Caregiver varchar(255),
    Patient varchar(255) REFERENCES Patient(Username),
    Vaccine varchar(255) REFERENCES Vaccines(Name),
    PRIMARY KEY (ID),
    FOREIGN KEY (Time, Caregiver) REFERENCES Availabilities(Time, Username)
);