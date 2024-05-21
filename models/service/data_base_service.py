from sqlalchemy import create_engine, Column, Integer, String, Float, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import datetime

# Datos de conexión
DATABASE_URI = "mssql+pyodbc://dataadmin:Antorcha.27@datacode-srv.database.windows.net/databasename?driver=ODBC+Driver+17+for+SQL+Server"

# Crear el motor de conexión
engine = create_engine(DATABASE_URI)

# Crear la base declarativa
Base = declarative_base()

# Definir el modelo de la tabla
class Transaction(Base):
    __tablename__ = 'hired_employees'
    id = Column(Integer, primary_key=True, autoincrement=True)
    transaction_id = Column(String, unique=True, nullable=False)
    amount = Column(Float, nullable=False)
    currency = Column(String, nullable=False)
    date = Column(Date, nullable=False)

# Crear la tabla en la base de datos
Base.metadata.create_all(engine)

# Crear una sesión
Session = sessionmaker(bind=engine)
session = Session()

# Crear un nuevo registro
new_transaction = Transaction(
    transaction_id="TX123456",
    amount=100.50,
    currency="USD",
    date=datetime.date(2023, 5, 20)
)

# Agregar el nuevo registro a la sesión y confirmar la transacción
try:
    session.add(new_transaction)
    session.commit()
    print("Registro insertado exitosamente.")
except Exception as e:
    session.rollback()
    print(f"Error al insertar el registro: {e}")
finally:
    session.close()
