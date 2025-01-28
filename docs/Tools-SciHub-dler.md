<div align="center">

# 📥 SciHub Downloader System

*Automated scientific paper downloader using Sci-Hub*

</div>

## Overview
SciHub Downloader is a tool for automatically downloading academic papers using Sci-Hub. It handles DOI resolution, PDF downloading, and metadata updates in the database.

## ✨ Features
- 🔍 Automatic DOI Resolution
- 📑 PDF Download Management
- 🗃️ Metadata Integration
- 💾 File Name Sanitization
- 🔄 Automatic Retry System
- ⚡ Progress Tracking
- 📁 Organized File Storage

## Class Structure

### SciHubDler
Main class handling paper downloads from Sci-Hub.

#### Methods
- `download_paper(doi: str, title: str, metadata_id: int, scihub_url: str, download_dir: str) -> bool`:
  - Resolves DOI on Sci-Hub
  - Extracts PDF download link
  - Downloads and saves paper
  - Updates metadata status
  - Returns success status

### Helper Functions

#### sanitize_filename
- `sanitize_filename(filename: str) -> str`:
  - Removes invalid characters
  - Truncates to 255 characters
  - Ensures cross-platform compatibility

## Technical Details

### 🔍 PDF Detection Methods
Tries multiple selectors for PDF links:
- Download buttons
- Direct PDF links
- Embedded PDF viewers
- IFrame elements

### 🛡️ Error Handling
- Network request errors
- Invalid DOIs
- Missing PDFs
- File system errors
- Database update failures

### ⏱️ Rate Limiting
- 3-second delay between downloads
- Timeout settings for requests
- Connection error handling

## Setup

### ⚙️ Environment Settings
Required in `.env`:
```env
postgresdb=your_db_name
postgresusername=your_username
postgrespassword=your_password
postgreshost=your_host
postgresport=your_port