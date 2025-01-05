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
        
    def get_paper_sources(self, project_name: str, session_ids: list[int]) -> list:
        """
        Get paper sources for a given project and session IDs
        
        Args:
            project_name (str): Name of the project
            session_ids (list[int]): List of session IDs"""
        
        try:
            with self.conn.cursor() as cursor:
                # Convert session_ids to tuple for SQL IN clause
                session_ids_tuple = tuple(session_ids)
                
                # Adjust query based on number of session IDs
                if len(session_ids) == 1:
                    cursor.execute("""
                        SELECT sh.answer FROM ai_schema.summaries_history sh
                        WHERE projectname = %s 
                        AND sessionid = %s
                    """, (project_name, session_ids[0]))
                else:
                    cursor.execute("""
                        SELECT sh.answer FROM ai_schema.summaries_history sh
                        WHERE projectname = %s 
                        AND sessionid IN %s
                    """, (project_name, session_ids_tuple))
                    
                paper_sources = cursor.fetchall()
                logger.info(ScriptIdentifier.DATABASE, 
                        f"Retrieved {len(paper_sources)} records for project {project_name}")
                cursor.close()
                logger.info(ScriptIdentifier.DATABASE, f"Connection Closed.")
                return paper_sources
            
        except Exception as e:
            logger.error(ScriptIdentifier.DATABASE, 
                        f"Error getting paper sources for project {project_name}: {e}")
            cursor.close()
            logger.info(ScriptIdentifier.DATABASE, f"Connection Closed.")