def copycontent(enabled, new_input, existing_text, chapter_separator):
    if(enabled == False):
        return
    if(chapter_separator != ""):
        return existing_text+new_input+chapter_separator
    else:
        return existing_text+new_input
    
def copy_string(string):
    return string

