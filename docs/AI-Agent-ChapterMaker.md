# AI Agent ChapterMaker Documentation

## Table of Contents
- [Overview](#overview)
- [Requirements](#requirements)
- [Configuration](#configuration)
- [Core Components](#core-components)
- [Features](#features)
- [Usage](#usage)S
- [Directory Structure](#directory-structure)
- [Error Handling](#error-handling)

## Overview
The AI Agent ChapterMaker processes summarized texts into structured chapters using various AI models. It handles batch processing of large texts, maintains context across batches, and synthesizes final chapters. It comes as a follow-up to the outline generation process and serves as a bridge between raw data of summarized pfs and structured content.

## Requirements

### Software Dependencies
- Python 3.8+

### Required Packages
```plaintext
openai~=1.0.0
google-generativeai~=0.3.0
tiktoken~=0.5.0
python-dotenv~=1.0.0
```
## Configuration

### Environment Variables
```plaintext
OPENAI_API_KEY=your_openai_api_key
DEEPSEEK_API_KEY=your_deepseek_api_key
```


## Core Components
1. BatchChapterMaker <br>
Base class handling batch processing:

```python
maker = BatchChapterMaker()
maker.make_chapter()
```

2. Model-Specific Makers <br>
DeepSeekChapterMaker <br>
ChatGPTChapterMaker <br>
GeminiChapterMaker (pending)

## Features

### 🔄 Batch Processing

Token-aware text splitting <br>
Response caching <br>
Synthesis of batches <br>

### 🤖 Multi-model Support

OpenAI GPT models <br>
DeepSeek AI <br>
Future Gemini support <br>

### 📝 Processing Pipeline

Text splitting => Batch processing => Response caching => Final synthesis

## Directory Structure

```plaintext
project/
├── 📁 resources/
│   ├── 📁 output_of_ai/
│   │   └── 📄 chapters.txt
│   └── 📁 prompt-engineering/
│       ├── 📄 chapter_role.txt
│       ├── 📄 chapter_prompt.txt
│       └── 📄 synthesis_prompt.txt
```

## Usage Example

```python
from src.agents.chapter_maker import DeepSeekChapterMaker

# Initialize maker
maker = DeepSeekChapterMaker()

# Process chapters
maker.make_chapter()
```

## Error Handling

✓ Retry mechanism for failed batches <br>
✓ JSON response validation <br>
✓ Response cleaning <br>
✓ Comprehensive logging <br>
✓ Batch failure recovery <br>
