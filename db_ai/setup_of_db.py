import os
import psycopg2
from dotenv import load_dotenv

load_dotenv('.env')

def run_sql_script(script_path, dbname, user, password, host, port):
    try:
        # Connect to the default database to create the new database
        conn = psycopg2.connect(dbname="postgres", user=user, password=password, host=host, port=port)
        conn.autocommit = True
        with conn.cursor() as cursor:
            with open(script_path, 'r') as file:
                sql_commands = file.read()
                cursor.execute(sql_commands)
        print("SQL script executed successfully.")
    except Exception as e:
        print(f"Error executing SQL script: {e}")
    finally:
        if conn:
            conn.close()


# Connect to the new database and run the setup_of_db.sql script
run_sql_script("db_ai/setup_of_db.sql",
               dbname=os.getenv('postgresdb'),
               user=os.getenv('postgresusername'),
               password=os.getenv('postgrespassword'), 
               host=os.getenv('postgreshost'), 
               port=os.getenv('postgresport'))