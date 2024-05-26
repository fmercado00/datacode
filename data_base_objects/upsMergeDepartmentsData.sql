CREATE TYPE departmentstype as TABLE
(
	id INT,
	department VARCHAR(255)
)
GO

CREATE OR ALTER PROCEDURE [dbo].[upsMergeDepartmentsData](@source departmentstype READONLY)
AS
BEGIN
    MERGE INTO departments AS target
    USING (SELECT id AS id, department FROM @source) AS source
    ON target.id = source.id
    WHEN MATCHED THEN
        UPDATE SET target.department = source.department
    WHEN NOT MATCHED BY TARGET THEN
        INSERT (id, department)
        VALUES (source.id, source.department);
END;
GO