-- Description: This stored procedure merges hired employees into the database.
-- Parameters:
--   @id: The ID of the employee.
--   @name: The name of the employee.
--   @datetime: The date and time of the employee's hire.
--   @department_id: The ID of the department the employee belongs to.
--   @job_id: The ID of the job the employee holds.
CREATE OR ALTER PROCEDURE upsMergeHiredEmployees
@id int,
@name varchar(250),
@datetime varchar(23),
@department_id int,
@job_id int
AS
    IF EXISTS (SELECT * FROM hired_employees WHERE id = @id)
    BEGIN
        UPDATE hired_employees
        SET name = @name, datetime = @datetime, department_id = @department_id, job_id = @job_id
        WHERE id = @id
    END
    ELSE
    BEGIN
        INSERT INTO hired_employees (id, name, datetime, department_id, job_id)
        VALUES (@id, @name, CONVERT(DATETIME, @datetime, 126) , @department_id, @job_id)
    END

Go