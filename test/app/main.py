from sqlalchemy import create_engine, MetaData, text, Integer, String
from sqlalchemy.schema import Column, Table
from sqlalchemy.exc import SQLAlchemyError
from fastapi import FastAPI
from pydantic import BaseModel
import os

app = FastAPI()

mysql_user = "bXktdXNlcg=="  #os.getenv("MYSQL_USER", "default_user")
mysql_password = "bXktcm9vdC1wYXNzd29yZA=="  #os.getenv("MYSQL_PASSWORD", "default_password")
mysql_host = "mysql-service" #os.getenv("MYSQL_HOST", "mysql-service")
mysql_port = "3307" #os.getenv("MYSQL_PORT", "3306")
mysql_database = "bXktZGF0YWJhc2U="  #os.getenv("MYSQL_DATABASE", "default_database")

print(os.environ)

conn_string = f"mysql://{mysql_user}:{mysql_password}@{mysql_host}:{mysql_port}/{mysql_database}"

mysql_engine = create_engine(conn_string)

metadata = MetaData()

class TableSchema(BaseModel):
    table_name: str
    columns: dict

@app.get("/tables")
async def get_tables():
    with mysql_engine.connect() as connection:
        results = connection.execute(text('SHOW TABLES;'))
        dict_res = {}
        dict_res['database'] = [str(result[0]) for result in results.fetchall()]
        return dict_res

@app.put("/table")
async def create_table(schema: TableSchema):
    columns = [Column(col_name, eval(col_type)) for col_name, col_type in schema.columns.items()]
    table = Table(schema.table_name, metadata, *columns)
    try:
        metadata.create_all(mysql_engine, tables=[table], checkfirst=False)
        return f"{schema.table_name} successfully created"
    except SQLAlchemyError as e:
        return dict({"error_msg": str(e)})
