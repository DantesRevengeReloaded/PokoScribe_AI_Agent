from src.agents.ai_agent_summarizer import *
from src.pokoscribe.automation_get_resources import *

logger = PokoLogger()

"""
get_sources = GetSources()
get_sources.get_metadata
get_sources.filter_metadata()
get_sources.download_filtered_papers
"""

pokosummarizer = AIBotSummarizer()
pokosummarizer.chatgptsummerize()