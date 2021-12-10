-- - - - - - - - - - - - - - - - - - - -
-- SQL Statement test for Scheduler.py
-- - - - - - - - - - - - - - - - - - - -

SELECT * FROM Caregivers;
SELECT * FROM Patient;
SELECT * FROM Availabilities;
SELECT * FROM Vaccines;
SELECT * FROM Appointment;

INSERT INTO Availabilities (Time, Username)
VALUES ('2021-12-25', 'Doctor'),
       ('2021-12-24', 'Doctor'),
       ('2021-12-23', 'Doctor')

INSERT INTO Availabilities (Time, Username)
VALUES ('2021-12-23', 'Doctor')

SELECT DISTINCT Username
FROM Availabilities as A
WHERE '2021-12-25' = A.Time AND
      1 = A.Available

INSERT INTO Vaccines (Name, Doses)
VALUES ('Pfizer', 10),
       ('Moderna', 10),
       ('Johnson & Johnson', 5)

INSERT INTO Vaccines (Name, Doses) VALUES ('AstraZeneca', 0)

SELECT * FROM Vaccines
WHERE Doses > 0;

DELETE FROM Availabilities WHERE Username='Doctor' AND Time='2021-12-23'

SELECT COUNT(*) FROM Appointment

INSERT INTO Appointment (ID, Time, Caregiver, Patient, Vaccine)
VALUES (1, '2021-12-25', 'Doctor', 'Iris', 'Pfizer')

SELECT Doses FROM Vaccines
WHERE Name = 'Pfizer'

UPDATE Vaccines
SET Doses=1
WHERE Name='Pfizer'

UPDATE Availabilities
SET Available=0
WHERE Time = '2021-12-23' AND Username = 'Doctor'

SELECT *
FROM Appointment
WHERE Caregiver = 'Doctor'

SELECT Time, Caregiver, Patient
FROM Appointment
WHERE ID = 3

UPDATE Availabilities
SET Available=1
WHERE Time='2021-12-20'

DELETE FROM Appointment
WHERE ID = 1

INSERT INTO Availabilities (Time, Username, Available) VALUES ('2021-12-24', 'Strange', 1)

UPDATE Vaccines SET Doses=1 WHERE Name='Pfizer'

SELECT Doses FROM Vaccines WHERE Name='Pfizer'