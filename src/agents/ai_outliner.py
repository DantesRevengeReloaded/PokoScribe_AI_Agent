
import os, json, openai, sys
from openai import OpenAI
from typing import List, Dict
from dotenv import load_dotenv
from pathlib import Path
# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))
from logs.pokolog import PokoLogger, ScriptIdentifier
from src.tools.token_counter import *
from src.config import *
import google.generativeai as genai
from src.db_ai.ai_db_manager import *
logger = PokoLogger()

from concurrent.futures import ThreadPoolExecutor, as_completed

def initialize_parameters(model_type: str):
    try:
        global aiparameters, summparameters
        
        if model_type not in model_lists:
            raise ValueError(f"Invalid model type. Must be one of {model_lists}")
        
        if model_type == 'openai':
            aiparameters = ChatGPTPars()
            summparameters = ChatGPTPdfSummerizerPars()
        elif model_type == 'gemini':
            aiparameters = GeminiPars()
            summparameters = GeminiSummerizerPars()
        elif model_type == 'deepseek':
            aiparameters = DeepSeekPars()
            summparameters = DeepSeekSummerizerPars()
        
        if not aiparameters or not summparameters:
            logger.error(ScriptIdentifier.OUTLINER, "Failed to initialize AI parameters")
            raise RuntimeError("Failed to initialize AI parameters")
        logger.info(ScriptIdentifier.OUTLINER, "AI parameters initialized successfully.")
    except Exception as e:
        logger.error(ScriptIdentifier.OUTLINER, f"Error initializing parameters: {e}")
        raise
        
model_lists = SystemPars().model_lists

class PaperOutliner:
    def __init__ (self, model_type: str):
        self.model_type = model_type

        if model_type == 'openai':
            self.aiparameters = ChatGPTPars()
        elif model_type == 'gemini':
            self.aiparameters = GeminiPars()
        elif model_type == 'deepseek':
            self.aiparameters = DeepSeekPars()
        else:
            logger.warning(ScriptIdentifier.OUTLINER, f"Invalid model type. Not in supported list: {model_lists}")
            raise ValueError(f"Invalid model type. Not in supported list: {model_lists}")
        
        # Initialize token counter and get summary stats
        counter = TokenCounter()
        self.summary_stats = counter.count_summary()
        logger.info(ScriptIdentifier.OUTLINER, f"Summary stats: {self.summary_stats}")

class ChatGPTOutliner(PaperOutliner):
    def __init__(self):
        super().__init__()

    def generate_paper_outline():
        pass





class PaperStructureGenerator:
    def __init__(self, openai_api_key: str, summaries: List[str], batch_size: int = 10):
        """
        Initialize the Paper Structure Generator
        
        :param openai_api_key: OpenAI API key
        :param summaries: List of article summaries
        :param batch_size: Number of summaries to process in each batch
        """
        openai.api_key = openai_api_key
        self.summaries = summaries
        self.batch_size = batch_size
        self.model = "gpt-4-turbo"  # Use the latest GPT model
    
    def generate_initial_outlines(self) -> List[Dict]:
        """
        Generate initial paper outlines by processing summaries in batches
        
        :return: List of generated outlines
        """
        all_outlines = []
        
        # Split summaries into batches
        batches = [self.summaries[i:i + self.batch_size] 
                   for i in range(0, len(self.summaries), self.batch_size)]
        
        # Process batches in parallel
        with ThreadPoolExecutor(max_workers=5) as executor:
            future_to_batch = {
                executor.submit(self._generate_batch_outline, batch): batch 
                for batch in batches
            }
            
            for future in as_completed(future_to_batch):
                try:
                    outline = future.result()
                    all_outlines.append(outline)
                except Exception as exc:
                    print(f'Batch processing generated an exception: {exc}')
        
        return all_outlines
    
    def _generate_batch_outline(self, batch_summaries: List[str]) -> Dict:
        """
        Generate an outline for a batch of summaries
        
        :param batch_summaries: List of summaries in a batch
        :return: Proposed paper outline
        """
        prompt = f"""
        Analyze the following article summaries and propose a comprehensive paper outline:
        
        {' '.join(batch_summaries)}
        
        Based on these summaries, provide:
        1. Potential main chapters
        2. Suggested sub-sections
        3. Rationale for the structure
        
        Return the response as a JSON with keys: 
        - 'chapters': list of chapter titles
        - 'sections': dict of chapters and their subsections
        - 'rationale': explanation of the proposed structure
        """
        
        response = openai.ChatCompletion.create(
            model=self.model,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": "You are an expert academic paper structure analyzer."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1000
        )
        
        return json.loads(response.choices[0].message.content)
    
    def synthesize_final_outline(self, initial_outlines: List[Dict]) -> Dict:
        """
        Synthesize a final paper outline from multiple initial outlines
        
        :param initial_outlines: List of preliminary outlines
        :return: Consolidated final outline
        """
        synthesis_prompt = f"""
        Synthesize the most coherent paper structure from these proposed outlines:
        
        {json.dumps(initial_outlines, indent=2)}
        
        Merge similar chapters, resolve conflicts, and create a unified, logical structure.
        
        Return as JSON with:
        - 'final_chapters': Consolidated chapter list
        - 'final_sections': Merged section structure
        - 'synthesis_rationale': Explanation of how the final outline was derived
        """
        
        response = openai.ChatCompletion.create(
            model=self.model,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": "You are an expert at academic paper structure synthesis."},
                {"role": "user", "content": synthesis_prompt}
            ],
            max_tokens=1000
        )
        
        return json.loads(response.choices[0].message.content)
    
    def generate_paper_structure(self) -> Dict:
        """
        Main method to generate the paper structure
        
        :return: Final paper structure
        """
        # Generate initial outlines
        initial_outlines = self.generate_initial_outlines()
        
        # Synthesize final outline
        final_structure = self.synthesize_final_outline(initial_outlines)
        
        return final_structure

def main():
    # Example usage
    openai_api_key = os.getenv('OPENAI_API_KEY')
    
    # Placeholder for 100 article summaries
    summaries = [f"Summary of article {i}" for i in range(100)]
    
    generator = PaperStructureGenerator(openai_api_key, summaries)
    paper_structure = generator.generate_paper_structure()
    
    print(json.dumps(paper_structure, indent=2))


    

tk = PaperOutliner('openai')