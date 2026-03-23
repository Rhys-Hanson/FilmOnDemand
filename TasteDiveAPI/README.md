# TasteDive API - Seed Selection Module

**Author:** Anish Jami (`ajami558`)  
**Project:** Film On Demand (Group 10)  
**Phase:** 1 - Individual API Implementation

## Purpose

This module uses the [TasteDive API](https://tastedive.com/account/api_access) to generate an initial list of movie recommendations by finding titles similar to movies a user already enjoys. This serves as the **Seed Selection** step in the Film On Demand pipeline.

## Setup

1. **Install dependencies:**
   ```bash
   cd TasteDiveAPI
   pip install -r requirements.txt
   ```

2. **Configure API Key:**
   ```bash
   cp .env.example .env
   ```
   Edit `.env` and replace `your_api_key_here` with your TasteDive API key.  
   Get a free key at: https://tastedive.com/account/api_access

## Usage

### Interactive Mode
```bash
python main.py
```

### One-Shot Mode (pass movie as argument)
```bash
python main.py "The Dark Knight"
python main.py "Inception, Interstellar"
```

## Features

- Search for similar movies by title
- Search with multiple seed movies at once
- Adjustable number of results
- Displays descriptions and YouTube links for recommendations
- Quick demo mode with preset movies
