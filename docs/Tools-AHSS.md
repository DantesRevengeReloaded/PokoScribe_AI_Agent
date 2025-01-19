<div align="center">

# 🔍 Academic Hyper Search System (AHSS)

*An intelligent academic paper search and analysis tool*

</div>

## Overview
AHSS is a tool for searching academic resources across multiple academic databases and APIS. After the extraction of metadata, the tool calculates a relevance score based on keyword matches and other factors and then data are stored in postgres database for later use. 

The tool supports the following databases:
- 🌐 CrossRef API Handler
- 🎓 OpenAlex API Handler
- 📖 CORE API Handler

## ✨ Features
- 📚 Multi-database Academic Search (CrossRef, OpenAlex, CORE)
- 🎯 Smart Relevance Scoring System
- 📊 Metadata Extraction & Analysis
- 💾 Database Integration & Storage
- 🔄 Cross-Platform Compatibility
- ⚡ Real-time Processing
- 🔍 Advanced Keyword Filtering

## Class Structure

### AHSS (Abstract Base Class)
Base class implementing common functionality:
- Relevance scoring
- Column definitions
- Keyword management

#### Methods
- `calculate_relevance_score(work: Dict) -> float`: Calculates paper relevance based on:
  - Title matches (3 points)
  - Abstract matches (2 points)
  - Publication year (recency bonus)
  - Citation count (up to 2 points)

### 🌐 CrossRefHandler
Handles interactions with CrossRef API.

#### Methods
- `search_resources(results_per_keyword: int = 50, from_year: Optional[int] = None) -> pd.DataFrame`
  - Searches CrossRef database
  - Supports year filtering
  - Returns DataFrame with metadata

### 🎓 OpenAlexHandler
Manages OpenAlex API searches.

#### Methods
- `search_resources(results_per_keyword: int = 50) -> pd.DataFrame`
  - Searches OpenAlex database
  - Extracts author information
  - Returns standardized metadata

### 📖 CoreAPIHandler
Interfaces with CORE API.

#### Methods
- `search_specific_papers() -> List[Dict]`
  - Uses enhanced query building
  - Supports keyword filtering
  - Returns filtered paper metadata

## Setup

### ⚙️ Environment Settings
Required in `.env`:
```env
MY_MAIL=your.email@domain.com
CORE_API_KEY=your_core_api_key