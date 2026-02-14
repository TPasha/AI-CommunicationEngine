#!/usr/bin/env python3
"""Fix class= to className= in JSX code."""
import re

html_path = r'd:\AI Communication Engine\mvp\templates\index.html'

# Read the file
with open(html_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Split by the babel script tag
before_script = content[:content.find('<script type="text/babel">')]
script_start = content.find('<script type="text/babel">')
script_end = content.find('</script>', script_start)
jsx_code = content[script_start:script_end]
after_script = content[script_end:]

# Replace class= with className= in JSX code only
# This regex looks for class= (with space before and after)
jsx_fixed = re.sub(r' class=', ' className=', jsx_code)

# Write back
fixed_content = before_script + jsx_fixed + after_script

with open(html_path, 'w', encoding='utf-8') as f:
    f.write(fixed_content)

# Count changes
original_count = jsx_code.count(' class=')
print(f"✅ Fixed {original_count} instances of 'class=' to 'className=' in JSX code")
print(f"File saved: {html_path}")
