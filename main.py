from fastapi import FastAPI, HTTPException, Query, UploadFile, File
import uvicorn
from utils.seo_optimizer import SEOOptimizer
from utils.file_handler import FileHandler
from configparser import ConfigParser
from fastapi.responses import StreamingResponse
import requests
import io
from typing import Optional

app = FastAPI()

@app.post("/optimize-seo/")
async def optimize_seo(
    key: str = Query(default='Insert here your password'), 
    openai_api_key: str =  Query(default='Insert here your OpenAPI Key'),
    input_file: UploadFile = File(None),
    language: str = Query(default='English'), 
    rules: Optional[UploadFile] = File(None), 
    title_rules_file: Optional[UploadFile] = File(None), 
    description_rules_file: Optional[UploadFile] = File(None), 
    additional_columns: Optional[str] = Query(default=None)
    ):
    config = ConfigParser()
    config.read('config.ini')
    default_language = config['DEFAULT']['language']
    key_config = config['DEFAULT']['auth_key']
    if (key == key_config):    
        # Handle language and rules
        language = language if language else default_language
        try:
            with open(rules.file, "rb") as f:
                writing_rules = f.read()
        except:
            writing_rules = open('setup/rules.txt','r').read()

        try:
            with open(title_rules_file.file, "rb") as f:
                title_rules = f.read()
        except:
            title_rules = open('setup/title-rules.txt', 'r').read()

        try:
            with open(description_rules_file.file, "rb") as f:
                description_rules = f.read()
        except:
            description_rules = open('setup/description-rules.txt', 'r').read()
        
        # Handle CSV file
        file_path = 'setup/input-file.csv' if not input_file.file else input_file.file
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
        seo_optimizer = SEOOptimizer(language, writing_rules,title_rules,description_rules,openai_api_key)
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

        buffer = io.StringIO()
        df.to_csv(buffer, index=False)
        buffer.seek(0) 
        return StreamingResponse(io.BytesIO(buffer.getvalue().encode()), media_type="text/csv", headers={"Content-Disposition": "attachment; filename=exported_dataframe.csv"})
        
    else:
        raise HTTPException(status_code=400, detail="Wrong Password")
    

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
