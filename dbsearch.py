import pyodbc
from PyQt6 import *

def connect_to_sql_server():
    server = 'RIZA'  # Update with your server name
    database = 'DSC-OIT'  # Update with your database name
    username = 'sa'  # Update with your username
    password = '78963'  # Update with your password

    connection_string = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password}'
    try:
        connection = pyodbc.connect(connection_string)
        print("Connection successful")
        return connection
    except Exception as e:
        print(f"Error connecting to SQL Server: {e}")
        return None

def list_test_ana(connection):
            if connection is None:
                print("No connection to SQL Server.")
                return
            
            cursor = connection.cursor()
            try:
                cursor.execute("SELECT * FROM dbo.TestAna")
                rows = cursor.fetchall()
                for row in rows:
                    print(row)
            except Exception as e:
                print(f"Error retrieving data from dbo.TestAna: {e}")
            finally:
                cursor.close()


list_test_ana(connect_to_sql_server())