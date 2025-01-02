-- Create schema
CREATE SCHEMA IF NOT EXISTS ai_schema;

-- Create table in the schema
CREATE TABLE IF NOT EXISTS ai_schema.ai_db_history (
    id SERIAL PRIMARY KEY,
    prompt TEXT,
    fileeditedname VARCHAR(255),
    tokencountprompt INT,
    answer TEXT,
    tokencountanswer INT,
    timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    model VARCHAR(50) NOT NULL,
    type_of_prompt VARCHAR(50) NOT NULL
);