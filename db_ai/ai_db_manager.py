import psycopg2
from psycopg2 import sql
from dotenv import load_dotenv
import os

load_dotenv('.env')

class AIDbManager:
    def __init__(self):
        self.conn = None
        try:
            self.conn = psycopg2.connect(
                dbname=os.getenv('postgresdb'),
                user=os.getenv('postgresusername'),
                password=os.getenv('postgrespassword'),
                host=os.getenv('postgreshost'),
                port=os.getenv('postgresport')
            )
            self.conn.autocommit = True
            print("Database connection established.")
        except Exception as e:
            print(f"Error connecting to the database: {e}")

    def insert_row(self, 
                        projectname, sessionid, prompt, 
                        fileeditedname, tokencountprompt, answer, 
                        tokencountanswer, model, modeldetails, type_of_prompt):
        
        try:
            with self.conn.cursor() as cursor:
                insert_query = sql.SQL("""
                    INSERT INTO ai_schema.summaries_history (
                        projectname, sessionid, prompt, fileeditedname, tokencountprompt, answer, tokencountanswer, model, modeldetails, type_of_prompt
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """)
                cursor.execute(insert_query, (projectname, sessionid, prompt, fileeditedname, tokencountprompt, answer, tokencountanswer, model, modeldetails, type_of_prompt))
                print("Row inserted successfully.")
        except Exception as e:
            print(f"Error inserting row: {e}")

    def close(self):
        if self.conn:
            self.conn.close()
            print("Database connection closed.")