#!/usr/bin/env python3
import re

# Read the current ai_task_service.py file
with open('/app/backend/ai_task_service.py', 'r', encoding='utf-8') as file:
    content = file.read()

def trim_message_category(content, start_marker, end_marker):
    """Trim a message category to 90 messages instead of 150"""
    
    # Find the start of the category
    start_pos = content.find(start_marker)
    if start_pos == -1:
        print(f"Could not find {start_marker}")
        return content
    
    # Find the end of the category
    end_pos = content.find(end_marker, start_pos)
    if end_pos == -1:
        print(f"Could not find {end_marker}")
        return content
    
    # Extract the category section
    category_section = content[start_pos:end_pos]
    
    # Split into lines and find message lines (lines with quotes)
    lines = category_section.split('\n')
    message_lines = []
    other_lines = []
    
    for line in lines:
        if '"' in line and line.strip().endswith(',') and not line.strip().startswith('#'):
            message_lines.append(line)
        else:
            other_lines.append(line)
    
    # Take only first 90 messages (18 messages per subcategory × 5 subcategories)
    messages_per_subcategory = 18
    subcategories = ["good_morning", "good_night", "love_confession", "apology", "funny_hinglish"]
    
    trimmed_messages = []
    current_subcategory = 0
    messages_in_current = 0
    
    in_list = False
    for line in lines:
        if '"' in line and line.strip().endswith(',') and not line.strip().startswith('#'):
            if not in_list:
                in_list = True
                messages_in_current = 0
                
            if messages_in_current < messages_per_subcategory:
                trimmed_messages.append(line)
                messages_in_current += 1
        elif line.strip().startswith(']') and in_list:
            # End of current subcategory
            trimmed_messages.append(line)
            in_list = False
            current_subcategory += 1
            if current_subcategory >= len(subcategories):
                break
        elif not in_list or messages_in_current < messages_per_subcategory:
            trimmed_messages.append(line)
    
    # Reconstruct the category section
    new_category_section = '\n'.join(trimmed_messages)
    
    # Replace in the original content
    new_content = content[:start_pos] + new_category_section + content[end_pos:]
    
    return new_content

print("Trimming DAILY_MEETUP_MESSAGES...")
content = trim_message_category(content, "DAILY_MEETUP_MESSAGES = {", "LONG_DISTANCE_MESSAGES = {")

print("Trimming LONG_DISTANCE_MESSAGES...")  
content = trim_message_category(content, "LONG_DISTANCE_MESSAGES = {", "SAME_HOME_MESSAGES = {")

print("Trimming SAME_HOME_MESSAGES...")
content = trim_message_category(content, "SAME_HOME_MESSAGES = {", "class AITaskService:")

# Write the modified content back
with open('/app/backend/ai_task_service.py', 'w', encoding='utf-8') as file:
    file.write(content)

print("✅ Successfully trimmed all message categories to 90 messages each (18 per subcategory)!")