-- Create schema
CREATE SCHEMA IF NOT EXISTS ai_schema;

-- Create table in the schema
CREATE TABLE IF NOT EXISTS ai_schema.summaries_history (
    id SERIAL PRIMARY KEY,
    projectname VARCHAR(255) NOT NULL,
    sessionid INT NOT NULL,
    prompt TEXT,
    fileeditedname TEXT,
    tokencountprompt INT,
    answer TEXT,
    tokencountanswer INT,
    timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    model VARCHAR(255) NOT NULL,
    modeldetails TEXT NOT NULL,
    type_of_prompt VARCHAR(255) NOT NULL,
    citation TEXT
);