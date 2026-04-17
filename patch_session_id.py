#!/usr/bin/env python3
"""Patch get_active_session_id to exclude cron sessions"""

patch_script = '''
import re

with open('/root/.openclaw/workspace/soul-memory/heartbeat-trigger.py', 'r') as f:
    lines = f.readlines()

# Find the function and add the cron filter
new_lines = []
i = 0
while i < len(lines):
    line = lines[i]
    new_lines.append(line)
    
    # Insert after "for key, data in sessions.items():"
    if 'for key, data in sessions.items():' in line:
        # Add indentation
        indent = '                '
        new_lines.append(indent + '# v3.5.7: 排除 cron session\\n')
        i += 1
        new_lines.append(lines[i])  # if isinstance line
        i += 1
        new_lines.append(lines[i])  # updatedAt line
        i += 1
        # Add the cron filter before the time check
        new_lines.append(indent + 'if \"cron\" in key.lower():\\n')
        new_lines.append(indent + '    continue\\n')
        continue
    
    i += 1

with open('/root/.openclaw/workspace/soul-memory/heartbeat-trigger.py', 'w') as f:
    f.writelines(new_lines)

print("Patched successfully")
'''

exec(patch_script)