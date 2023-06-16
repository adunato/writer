from .writer_utils import copycontent, copy_string, get_matching_file_path, read_file_to_string
from modules.text_generation import generate_reply_wrapper

def _summarise_content(content, summarisation_template, state):
    summarisation_file = get_matching_file_path(summarisation_template)
    if(summarisation_file == ""):
        print(f"No teplate file found for {summarisation_template}")
        return ""
    instruction = read_file_to_string(summarisation_file)
    instruction = instruction.replace("{content}", content)

    outputcontent = ""

    for result in generate_reply_wrapper(instruction, state):
        outputcontent += result[0]

    outputcontent = outputcontent.replace(instruction, "")

    return outputcontent

def add_summarised_content(content, text_box, summarisation_template, state, summarisation_enabled, replace=False, add_cr=True):
    if(summarisation_enabled == False):
        return ""
    summarised_content = _summarise_content(content, summarisation_template, state)
    if(replace):
        text_box = summarised_content
    else:
        text_box += summarised_content
    if(add_cr):
        text_box+="\n\n"
    return text_box
