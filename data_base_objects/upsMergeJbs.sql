/*
	Procedure Name: upsMergeJobs
	Description: This stored procedure is used to merge or update the job field in the jobs table based on the provided id.
	Parameters:
		- @id (int): The id of the job to be updated or inserted.
		- @job (varchar(250)): The new job value to be updated or inserted.
	Returns: None
*/

CREATE OR ALTER PROCEDURE upsMergeJobs
@id int,
@job varchar(250)
AS
	IF EXISTS (SELECT * FROM jobs WHERE id = @id)
	BEGIN
		UPDATE jobs
		SET job = @job
		WHERE id = @id
	END
	ELSE
	BEGIN
		INSERT INTO jobs (id, job)
		VALUES (@id, @job)
	END
Go
