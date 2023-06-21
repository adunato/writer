from pathlib import Path
from modules import utils
from .writer_params import input_elements

def copycontent(enabled, new_input, existing_text, chapter_separator):
    if(enabled == False):
        return ""
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

def copy_prompt_analysis_output(text_boxA, prompt_analysis, token_count):
    return prompt_analysis

def copy_args(*args):
    print(f"args:{args}")
    return args

def get_available_templates():
    paths = (x for x in Path('extensions/writer/templates').iterdir() if x.suffix in ('.txt'))
    return ['None'] + sorted(set((k.stem for k in paths)), key=utils.natural_keys)

def gather_interface_values(*args):
    output = {}
    for i, element in enumerate(input_elements):
        output[element] = args[i]

    return output
