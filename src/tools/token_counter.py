import tiktoken
import pandas as pd
import json
from pathlib import Path
from PyPDF2 import PdfReader
import os

class TokenCounter:
    def __init__(self, model="gpt-3.5-turbo"):
        self.encoding = tiktoken.encoding_for_model(model)
        
    def count_tokens(self, text: str) -> int:
        """Count tokens in a text string"""
        return len(self.encoding.encode(text))
    
    def count_pdf(self, file_path: str) -> dict:
        """Count tokens in a PDF file"""
        reader = PdfReader(file_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
        
        tokens = self.count_tokens(text)
        return {
            'file': os.path.basename(file_path),
            'tokens': tokens,
            'pages': len(reader.pages),
            'tokens_per_page': tokens / len(reader.pages)
        }
    
    def count_csv(self, file_path: str) -> dict:
        """Count tokens in a CSV file"""
        df = pd.read_csv(file_path)
        total_tokens = 0
        column_tokens = {}
        
        for column in df.columns:
            column_text = df[column].astype(str).str.cat(sep=' ')
            tokens = self.count_tokens(column_text)
            column_tokens[column] = tokens
            total_tokens += tokens
            
        return {
            'file': os.path.basename(file_path),
            'total_tokens': total_tokens,
            'rows': len(df),
            'columns': len(df.columns),
            'tokens_per_column': column_tokens,
            'avg_tokens_per_row': total_tokens / len(df)
        }
    
    def count_text(self, file_path: str) -> dict:
        """Count tokens in a text file"""
        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read()
        tokens = self.count_tokens(text)
        return {
            'file': os.path.basename(file_path),
            'tokens': tokens,
            'characters': len(text),
            'lines': text.count('\n') + 1
        }
    
    def count_json(self, file_path: str) -> dict:
        """Count tokens in a JSON file"""
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        text = json.dumps(data)
        tokens = self.count_tokens(text)
        return {
            'file': os.path.basename(file_path),
            'tokens': tokens,
            'size': len(text),
            'top_level_keys': len(data) if isinstance(data, dict) else 'N/A'
        }
    
    def count_file(self, file_path: str) -> dict:
        """Count tokens in any supported file type"""
        file_type = Path(file_path).suffix.lower()
        
        if file_type == '.pdf':
            return self.count_pdf(file_path)
        elif file_type == '.csv':
            return self.count_csv(file_path)
        elif file_type == '.txt':
            return self.count_text(file_path)
        elif file_type == '.json':
            return self.count_json(file_path)
        else:
            raise ValueError(f"Unsupported file type: {file_type}")

def main():
    counter = TokenCounter()
    
    # Example usage
    files = [
        'merged_results.csv'
    ]
    
    for file in files:
        if os.path.exists(file):
            try:
                result = counter.count_file(file)
                print(f"\nResults for {file}:")
                for key, value in result.items():
                    print(f"{key}: {value}")
            except Exception as e:
                print(f"Error processing {file}: {e}")

if __name__ == "__main__":
    main()