CREATE TYPE jobstype as TABLE
(
	id INT,
	job VARCHAR(255)
)
GO

CREATE OR ALTER PROCEDURE [dbo].[upsMergeJobsData](@source jobstype READONLY)
AS
BEGIN
    MERGE INTO jobs AS target
    USING (SELECT id AS id, job FROM @source) AS source
    ON target.id = source.id
    WHEN MATCHED THEN
        UPDATE SET target.job = source.job
    WHEN NOT MATCHED BY TARGET THEN
        INSERT (id, job)
        VALUES (source.id, source.job);
END;
GO