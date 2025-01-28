<div align="center">

# 🔢 Token Counter System

*Multi-format token counting utility for AI text processing*

</div>

## Overview
Token Counter is a versatile utility for counting tokens in various file formats. It handles multiple encodings, provides detailed metrics, and supports different AI models.

## ✨ Features
- 📊 Multi-format Support (PDF, CSV, TXT, JSON)
- 🔡 Robust Encoding Handling
- 📈 Detailed Metrics
- 🔄 Model-specific Token Counting
- 🛡️ Error Recovery
- 📝 Logging System
- 📊 Statistics Generation

## Class Structure

### TokenCounter
Main class handling token counting across different formats.

#### Core Methods
- `count_tokens(text: str) -> int`:
  - Counts tokens in raw text
  - Model-specific encoding
  - Basic token metrics

#### File-Specific Methods
- `count_pdf(file_path: str) -> dict`:
  - PDF text extraction
  - Page-wise counting
  - Per-page token metrics

- `count_csv(file_path: str) -> dict`:
  - Column-wise counting
  - Row statistics
  - Aggregated metrics

- `count_text(file_path: str) -> dict`:
  - Multi-encoding support
  - Character counting
  - Line statistics

- `count_json(file_path: str) -> dict`:
  - Structure analysis
  - Key counting
  - Size metrics

## Technical Details

### 🔡 Encoding Support
- UTF-8
- UTF-8-SIG
- CP1252
- ISO-8859-1
- Latin1
- Binary fallback

### 📊 Metrics Provided
- Token count
- Character count
- Line count
- File size
- Format-specific metrics

### 🛡️ Error Handling
- Encoding errors
- File access issues
- Invalid formats
- Corrupt files
- Memory constraints

## Setup

### 📦 Dependencies
```plaintext
tiktoken
pandas
PyPDF2
```

## Directory Structure

```plaintext
src/
└── tools/
    └── token_counter.py
```

## Usage

```python
counter = TokenCounter(model="gpt-3.5-turbo")

# Count PDF tokens
pdf_stats = counter.count_pdf("document.pdf")

# Count text file tokens
text_stats = counter.count_text("text.txt")

# Count CSV tokens
csv_stats = counter.count_csv("data.csv")

# Count JSON tokens
json_stats = counter.count_json("config.json")
```