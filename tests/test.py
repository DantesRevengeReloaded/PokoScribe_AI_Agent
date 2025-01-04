import re
from pathlib import Path

# Use Path for proper file path handling
file_path = Path('prompts-roles/history/summary_total.txt')

try:
    with open(file_path, 'r') as fh:
        content = fh.read()
        # Use search() instead of findall() for first match only
        match = re.search(r'-\?!(.*?)-\?!', content)
        if match:
            daka = match.group(1) # group(1) gets the content inside the markers
        else:
            print("No markers found")
except FileNotFoundError:
    print(f"File not found: {file_path}")
except Exception as e:
    print(f"Error: {e}")

print(daka)