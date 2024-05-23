# Data Code Project Evaluation.


## Data Base Model.

erDiagram

    jobs {
        bigint id
        string job
    }

    departments {
        bigint id
        string department
    }

    hired_employees {
        bigint id
        string name
        datetime datetime
        bigint department_id
        bigint job_id
    }


    hired_employees ||..o{ jobs : "Hired Employee has a job"
    hired_employees ||..o{ departments : "Hired Employe has a department"
