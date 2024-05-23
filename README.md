# Data Code Project Evaluation.


## Data Base Model.

# Silver Sales Domain Model

The sales domain contains all the datasets required to do analytics on data belonging to the Sales Domain The datasets that we have in these domain are:

## Foundational

* Account
* Market Unit
* Opportunity
* Dynamics User

# Things to define

* TBD


# Silver Sales Domain Model

::: mermaid
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

:::