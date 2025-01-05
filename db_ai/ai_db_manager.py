import psycopg2
from psycopg2 import sql
from dotenv import load_dotenv
import os
from logs.pokolog import PokoLogger, ScriptIdentifier

load_dotenv('.env')

logger = PokoLogger()
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
            logger.info(ScriptIdentifier.DATABASE, "Connected to the database.")
            
        except Exception as e:
            logger.error(ScriptIdentifier.DATABASE, f"Error connecting to the database: {e}")

    def insert_row(self, 
                        projectname, sessionid, prompt, 
                        fileeditedname, tokencountprompt, answer, 
                        tokencountanswer, model, modeldetails, type_of_prompt, citation):
        
        try:
            with self.conn.cursor() as cursor:
                insert_query = sql.SQL("""
                    INSERT INTO ai_schema.summaries_history (
                        projectname, sessionid, prompt, fileeditedname, tokencountprompt, answer, tokencountanswer, model, modeldetails, type_of_prompt, citation
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """)
                cursor.execute(insert_query, (projectname, sessionid, prompt, fileeditedname, 
                                              tokencountprompt, answer, tokencountanswer, 
                                              model, modeldetails, type_of_prompt, citation))
                logger.info(ScriptIdentifier.DATABASE, f"Row for {fileeditedname} file inserted successfully.")
        except Exception as e:
            logger.error(ScriptIdentifier.DATABASE, f"Error inserting row {fileeditedname}: {e}")

    def close(self):
        if self.conn:
            self.conn.close()

    def get_last_session(self):
        try:
            with self.conn.cursor() as cursor:
                cursor.execute("SELECT MAX(sessionid) FROM ai_schema.summaries_history")
                last_session = cursor.fetchone()
                return last_session[0]
        except Exception as e:
            logger.error(ScriptIdentifier.DATABASE, f"Error getting last session: {e}")
            return None