FROM python:3.10-bullseye
RUN apt-get update && apt-get install -y unixodbc unixodbc-dev g++ libgssapi-krb5-2
RUN curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - \
    && curl https://packages.microsoft.com/config/debian/10/prod.list > /etc/apt/sources.list.d/mssql-release.list
RUN apt-get update \
    && ACCEPT_EULA=Y apt-get install -y msodbcsql17
WORKDIR /
COPY requirements.txt /requirements.txt
RUN pip install -r requirements.txt

EXPOSE 80
COPY . /
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]


