# SEO Optimizer

## Overview
This software optimizes SEO elements of given URLs using OpenAI's GPT-4. It supports CSV inputs with URL, Title, Description, (optional) Keywords, and additional columns. 

## Setup
1. Install requirements: `pip install fastapi uvicorn pandas openai requests`.
2. Place your `config.ini` in the root directory with OpenAI API key and default language.
3. Ensure `input-file.csv` and `rules.txt` are in the `setup` directory for default inputs.

## API Usage
- **Endpoint**: `/optimize-seo/`
- **Query Parameters**:
  - `file_url`: URL of the input CSV file.
  - `language`: Language for SEO optimization.
  - `rules_url`: URL of the text file containing writing rules.
  - `additional_columns`: Comma-separated names of additional columns to optimize.
- **Example Call**: `/optimize-seo?file_url=https://example.com/input.csv&language=en&rules_url=https://example.com/rules.txt&additional_columns=meta_tags,custom_tags`

## Notes
- The system validates required columns and handles errors gracefully.
- Optimizations consider language-specific rules and keyword emphasis where applicable.
- Outputs are saved in `output` directory with a timestamp.
