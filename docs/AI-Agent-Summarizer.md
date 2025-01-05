# AI Agent Summarization Documentation

## Table of Contents
- [Overview](#overview)
- [Requirements](#requirements)
- [Configuration](#configuration)
- [Core Components](#core-components)
- [Features](#features)
- [Database Schema](#database-schema)
- [Usage](#usage)
- [Directory Structure](#directory-structure)
- [Error Handling](#error-handling)


## Overview
The AI Agent Summarizer is part of a Multi-Agent System and it is a Python-based tool that processes PDF documents using various AI models (OpenAI, Gemini, DeepSeek) to generate summaries and citations. 

It includes database integration using postgres for storing results and supports chunking for large documents. The program is designed to handle multiple documents simultaneously, with comprehensive logging and error handling. 

The requirement is to define the folder paths so the agent will parse the PDF files and generate the summaries which will be stored to db so other agents of system can use it.

Prompt templates are used so the agent can generate the summaries based on the prompts and roles defined in the templates and also cite the sources with the desired style of citation (Harvard etc). The agent will generate the summaries and store them in the database for future use.

## Requirements

### Software Dependencies
- Python 3.8+

### Required Packages
```plaintext
openai~=1.0.0
google-generativeai~=0.3.0
PyPDF2~=3.0.0
tiktoken~=0.5.0
python-dotenv~=1.0.0
psycopg2~=2.9.9
```

## Configuration

### Environment Variables

Environment variables required in `.env`:

```properties
# AI Model API Keys 

OPENAI_API_KEY=your_openai_key = 
GEMINI_API_KEY=your_gemini_key = 
DEEPSEEK_API_KEY=your_deepseek_key =
```
### Database Configuration

Postgres is used for storing the summary history and other details. Its configuration is required for the agent to store the results.

Database connection details in `.env`:

```properties
# Postgres Database Configuration

postgresusername = 
postgrespassword = 
postgreshost = 
postgresport = 
postgresdb = 
```

### Folder Configuration

Folder paths in `config.py`:

```python
# Sample of folder paths that need to be configured

self.input_folder = 'data\summary_agent\input'
self.completed_folder = 'data\summary_agent\completed'

```

## Core Components

### 1. PDFReader

Handles PDF file reading and text extraction.

```python
reader = PDFReader(file_path)
text = reader.read()
```

### 2. AISummarizer

Manages AI model interactions and summary generation. The class is dependancy of PDFSummarizer and it is used to generate the summary of the text. It has the following features:

Supports multiple AI models  
Handles prompt management  
Includes citation extraction  

```python
summarizer = AISummarizer(api_key)
summerizer.summarize(text, worked_model)
```

### 3.  PDFSummarizer

Main class orchestrating the summarization process it is calld by the main file AI-Agent-Summarizer.py. It has the following features:

✓ PDF processing  
✓ Token counting  
✓ Chunking large documents  
✓ File management  
✓ Database integration

```python
pdf_summarizer = PDFSummarizer(input_folder, output_file, api_key, completed_folder, 
                 to_be_completed_folder, model_type)
pdf_summarizer.process_pdfs(workde_model)
```

## Features

🤖 Multi-model support (OpenAI, Gemini, DeepSeek)  
📄 Automatic text chunking for large documents  
📝 Citation extraction using markers (-?!text-?!)  
💾 Database storage of results  
📊 Comprehensive logging  
📁 File organization (completed/failed separations)  

## Database Schema

The database schema in postgres for storing summary history, citations, and other details. Especially token count is stored for each prompt and answer to keep track of the summarization process and cost:

```sql
CREATE TABLE ai_db_history (
    id SERIAL PRIMARY KEY,
    projectname VARCHAR(50) NOT NULL,
    sessionid INT NOT NULL,
    prompt TEXT,
    fileeditedname VARCHAR(255),
    tokencountprompt INT,
    answer TEXT,
    tokencountanswer INT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    model VARCHAR(50) NOT NULL,
    modeldetails VARCHAR(255) NOT NULL,
    type_of_prompt VARCHAR(50) NOT NULL,
    citation TEXT
);
```
## Usage

### Summarization Process

The specific AI Agent is called by the main file AI-Agent-Summarizer.py, which then processes the PDF files in the input folder and generates summaries using the selected AI model.

```python

from src.agents.AI-Agent-Summarizer import AIBotSummarizer

# Initialize summarizer
bot = AIBotSummarizer()

# Process with specific model
bot.chatgptsummerize()  # For OpenAI
bot.geminisummerize()   # For Gemini
bot.deepseeksummerize() # For DeepSeek
```
## Directory Structure

The directory structure for the AI Agent Summarization tool:<br>
data- Contains input, completed, and failed folders for the documents which are processed by the agent<br>
prompts-roles - Contains prompt templates for summarization<br>
history - Contains the total summary history file. The results are stored in the database as well<br>

```plaintext
project/
├── 📁 data/
│   └── 📁 summary_agent/
│       ├── 📁 input/
│       ├── 📁 completed/
│       └── 📁 failed/
├── 📁 prompts-roles/
│   ├── 📄 summarization_prompt.txt
│   ├── 📄 summarization_role.txt
│   └── 📄 summarization_citation.txt
└── 📁 history/
    └── 📄 summary_total.txt
```

## Error Handling

✓ Comprehensive logging system <br>
✓ Failed document management <br>
✓ Token limit handling <br>
✓ API error recovery<br>
