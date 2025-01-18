import tools_config
from tools_config import *
import ahs
from ahs import *


"""
# Define your search keywords
keywords = get_keywords()

# Run CrossRef search
handler = CrossRefHandler()
results_df = handler.search_resources(
    keywords=keywords,
    results_per_keyword=50,
    from_year=2020
)
# Save results
handler.save_results(results_df)
"""

queries_alex = get_keywords()
# Run OpenALEX search
alex_handler = OpenAlexHandler()
alex_handler.search_openalex(queries_alex, results_per_query=35)


