/*
    Procedure: upsMergeDepartments

    Description:
    This procedure is used to merge departments in the Departments table. If a department with the specified ID already exists, it will be updated with the new department name. Otherwise, a new department will be inserted into the table.

    Parameters:
    - @id (int): The ID of the department.
    - @department (varchar(250)): The name of the department.

    Returns:
    None.
*/
CREATE OR ALTER PROCEDURE upsMergeDepartments
@id int,
@department varchar(250)
AS
    IF EXISTS (SELECT * FROM Departments WHERE id = @id)
    BEGIN
        UPDATE Departments
        SET department = @department
        WHERE id = @id
    END
    ELSE
    BEGIN
        INSERT INTO Departments (id, department)
        VALUES (@id, @department)
    END
go