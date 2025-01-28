# AI Agent Outliner Documentation

## Table of Contents
- [Overview](#overview)
- [Requirements](#requirements)
- [Configuration](#configuration)
- [Core Components](#core-components)
- [Features](#features)
- [Usage](#usage)
- [Directory Structure](#directory-structure)
- [Error Handling](#error-handling)

## Overview
The AI Agent Outliner processes summarized texts to create structured outlines using various AI models. It handles large text with all summaries properly prepared from Agent-Summarizer. Then Outliner is splitting them into manageable batches and processes each batch independently so it can create a proposed outline based on viewed data.,In the end a final prompt synthesizes the final outline. 

Model support includes OpenAI GPT and DeepSeek AI, with future model integration to be added.

## Requirements

### Software Dependencies
- Python 3.8+
- Same package requirements as Summarizer

### Required Packages

```plaintext
openai~=1.0.0
google-generativeai~=0.3.0
tiktoken~=0.5.0
python-dotenv~=1.0.0
psycopg2~=2.9.9
```

## Configuration

### Environment Variables
 Variables required in `.env`
 Agent is configured in config.py file

## Core Components

### BatchOutliner

Base class handling text splitting and batch management:

Token counting <br>
Batch creation based on total tokens <br>
Response caching <br>
File handling <br>

### Model-Specific Outliners

DeepSeekOutliner <br>
ChatGPTOutliner <br>

Each handles specific API interactions

## Features

🔄 Batch Processing <br>
Splits large texts into manageable chunks <br>
Maintains token limits (default 25k tokens) <br>
Caches responses for synthesis <br>

📝 Multi-stage Processing <br>
Initial batch processing <br>
Final synthesis of all batches <br>
Comprehensive outline generation <br>

🤖 Multi-model Support <br>
OpenAI GPT models
DeepSeek AI
Future model integration ready

## Usage

```python
from src.agents.ai_outliner import DeepSeekOutliner, ChatGPTOutliner

# Using DeepSeek
outliner = DeepSeekOutliner()
outliner.outline_it()

# Using ChatGPT
gpt_outliner = ChatGPTOutliner()
gpt_outliner.outline_it()
```

## Directory Structure

```plaintext
project/
├── 📁 resources/
│   ├── 📁 output_of_ai/
│   │   └── 📄 outline.txt
│   └── 📁 prompt-engineering/
│       ├── 📄 outliner_role.txt
│       ├── 📄 single_batch_prompt.txt
│       └── 📄 final_synthesis_prompt.txt
```