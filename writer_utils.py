from pathlib import Path
def copycontent(enabled, new_input, existing_text, chapter_separator):
    if(enabled == False):
        return
    if(chapter_separator != ""):
        return existing_text+new_input+chapter_separator
    else:
        return existing_text+new_input
    
def copy_string(string):
    return string

def read_file_to_string(file_path):
    with open(file_path, 'r') as file:
        data = file.read()
    return data

def get_matching_file_path(filename):
    paths = (x for x in Path('extensions/writer/templates').iterdir() if x.suffix in ('.txt'))
    for path in paths:
        if path.stem == filename:
            return str(path)
    return ""

