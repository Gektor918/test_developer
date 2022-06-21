import psycopg2


class Config:
    '''
    Config class users 
    '''
    json_file = 'testdev-353506-0ad95667718d.json'
    id_doc = '1Ff9t0Kec_nyI4OBug-tljc4euUGGSUTpkLU-a4L8uPw'
    job_servis = ['https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive']


class Data_base:
    '''
    Config class datebase 
    (Version - 'PostgreSQL 10.21, compiled by Visual C++ build 1800, 32-bit',)
    '''
    create_table_query = '''CREATE TABLE if not exists TESTDEVSHEETS4
    (
    NUMBER  INT,
    PRICE   REAL,
    DATE    TEXT,
    PRICE_DOLLAR   REAL
    ); '''
    connection = psycopg2.connect(user="postgres", password="9187112",
    host="127.0.0.1", port="5432", database="testdb")