import tiktoken
import pandas as pd
import json
from pathlib import Path
from PyPDF2 import PdfReader
import os
from logs.pokolog import PokoLogger, ScriptIdentifier

logger = PokoLogger()

class TokenCounter:
    def __init__(self, model="gpt-3.5-turbo"):
        self.encoding = tiktoken.encoding_for_model(model)
        self.summary_file = "resources/output_of_ai/summary_total.txt"
        
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
        """Count tokens in a text file with robust encoding handling"""
        # List of encodings to try
        encodings = ['utf-8', 'utf-8-sig', 'cp1252', 'iso-8859-1', 'latin1']
        text = None
        
        # Try reading with different encodings
        for encoding in encodings:
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    text = f.read()
                logger.info(ScriptIdentifier.TOKENCOUNTER, f"Used {encoding} encoding")
                break
            except UnicodeDecodeError:
                logger.warning(ScriptIdentifier.TOKENCOUNTER, f"Failed to read with {encoding} encoding")
                continue
        
        # If all encodings fail, try binary read and decode
        if text is None:
            try:
                with open(file_path, 'rb') as f:
                    raw_bytes = f.read()
                    text = raw_bytes.decode('utf-8', errors='ignore')
                logger.info(ScriptIdentifier.TOKENCOUNTER, "Used binary read and decode")
            except Exception as e:
                raise ValueError(f"Could not read file with any encoding: {e}")
        
        tokens = self.count_tokens(text)
        result = {
            'file': os.path.basename(file_path),
            'tokens': tokens,
            'characters': len(text),
            'lines': text.count('\n') + 1,
            'encoding_used': encoding if text else 'binary',
            'status': 'success'
        }

        # Log detailed metrics
        logger.info(ScriptIdentifier.TOKENCOUNTER, 
                    f"File: {result['file']} | "
                    f"Tokens: {result['tokens']} | "
                    f"Chars: {result['characters']} | "
                    f"Lines: {result['lines']} | "
                    f"Encoding: {result['encoding_used']}")

        return result
    
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

    def count_summary(self) -> dict:
        """Count tokens in the summary file"""
        try:
            return self.count_text(self.summary_file)
        except Exception as e:
            return {
                'file': self.summary_file,
                'tokens': 0,
                'characters': 0,
                'lines': 0,
                'encoding_used': None
            }
        
    def safe_read_text(self, file_path: str) -> str:
        """Safely read text file with multiple encoding attempts"""
        encodings = ['utf-8', 'utf-8-sig', 'cp1252', 'iso-8859-1', 'latin1']
        
        for encoding in encodings:
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    text = f.read()
                logger.info(ScriptIdentifier.TOKENCOUNTER, 
                          f"Successfully read with {encoding}")
                return text
            except UnicodeDecodeError:
                continue
        
        # Fallback to binary read with ignore
        try:
            with open(file_path, 'rb') as f:
                text = f.read().decode('utf-8', errors='ignore')
            logger.info(ScriptIdentifier.TOKENCOUNTER, 
                       "Used binary read with ignore")
            return text
        except Exception as e:
            logger.error(ScriptIdentifier.TOKENCOUNTER, 
                        f"Failed to read file: {e}")
            raise