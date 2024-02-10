import pandas as pd
import datetime

class FileHandler:
    @staticmethod
    def read_csv(file_path, additional_columns=None):
        if additional_columns is None:
            additional_columns = []
        columns = ['URL', 'Title', 'Description'] + additional_columns
        try:
            df = pd.read_csv(file_path, usecols=lambda column: column in ['URL', 'Title', 'Description'] + additional_columns)
            
            if 'Keywords' in df.columns:
                df['Keywords'] = df['Keywords'].apply(lambda x: x.split(';') if pd.notnull(x) else [])
            
            return df
        except Exception as e:
            print(f"Error reading CSV file: {e}")
            return pd.DataFrame()

    @staticmethod
    def save_csv(df, prefix='output'):
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d-%H%M%S')
        output_path = f'output/{prefix}-{timestamp}.csv'
        df.to_csv(output_path, index=False)
        print(f"File saved to {output_path}")
