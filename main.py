from fastapi import FastAPI, HTTPException
import uvicorn
from utils.seo_optimizer import SEOOptimizer
from utils.file_handler import FileHandler
from configparser import ConfigParser
import requests

app = FastAPI()

@app.get("/optimize-seo/")
async def optimize_seo(file_url: str = None, language: str = None, rules_url: str = None, additional_columns: str = None):
    config = ConfigParser()
    config.read('config.ini')
    default_language = config['DEFAULT']['language']
    
    # Handle language and rules
    language = language if language else default_language
    writing_rules = requests.get(rules_url).text if rules_url else open('setup/rules.txt').read()
    title_rules = requests.get(rules_url).text if rules_url else open('setup/title-rules.txt').read()
    description_rules = requests.get(rules_url).text if rules_url else open('setup/rules.txt').read()
    # Handle CSV file
    file_path = 'setup/input-file.csv' if not file_url else file_url
    if additional_columns:
        additional_columns = additional_columns.split(',')
    else:
        additional_columns = []

    # Read CSV
    df = FileHandler.read_csv(file_path, additional_columns)
    if df.empty:
        raise HTTPException(status_code=404, detail="CSV file not found or missing required columns.")
    
    # Check columns
    required_columns = ['URL', 'Title', 'Description']
    if not all(column in df.columns for column in required_columns):
        raise HTTPException(status_code=400, detail="Missing one or more required columns: URL, Title, Description.")
    
    # SEO Optimization
    seo_optimizer = SEOOptimizer(language, writing_rules,title_rules,description_rules)
    for index, row in df.iterrows():
        # Basic optimization for 'Title' and 'Description'
        optimized_title = seo_optimizer.optimize_for_length(row['Title'], 'title', keywords=row.get('Keywords', []))
        optimized_description = seo_optimizer.optimize_for_length(row['Description'], 'description', keywords=row.get('Keywords', []))
        
        # Update DataFrame with optimized values
        df.at[index, 'Optimized Title'] = optimized_title
        df.at[index, 'Optimized Description'] = optimized_description
        
        # If there are additional columns to optimize, do so here
        for additional_column in additional_columns:
            if additional_column in df.columns:
                original_text = row[additional_column]
                optimized_text = seo_optimizer.optimize_text(original_text, keywords=row.get('Keywords', []))
                df.at[index, f'Optimized {additional_column}'] = optimized_text

    
    # Save the optimized DataFrame
    FileHandler.save_csv(df)
    
    return {"message": "SEO optimization completed", "file": file_path}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
