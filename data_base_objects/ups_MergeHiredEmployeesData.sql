CREATE TYPE hiredEmployeesType as TABLE
(
	[id] INT,
	[name] VARCHAR(255),
	[datetime] DATETIME,
	[department_id] INT ,
	[job_id] INT
)
GO
CREATE OR ALTER PROCEDURE [dbo].[upsMergeHiredEmployeesData](@source hiredEmployeesType READONLY)
AS
BEGIN
    MERGE INTO hired_employees AS target
    USING (SELECT id AS id, name, datetime, department_id, job_id FROM @source) AS source
    ON target.id = source.id
    WHEN MATCHED THEN
        UPDATE SET target.name = source.name
					,target.datetime = source.datetime
					,target.department_id = source.department_id
					,target.job_id = source.job_id
    WHEN NOT MATCHED BY TARGET THEN
        INSERT (id, name, datetime, department_id, job_id )
        VALUES (source.id, source.name, source.datetime, source.department_id, source.job_id );
END;