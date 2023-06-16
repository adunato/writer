from modules.text_generation import get_encoded_length
from .writer_utils import get_matching_file_path, read_file_to_string

def tag_prompt_elements(template_content, summary, question):
    output_spans = []
    length_summary = {"template": 0, "background": 0, "user_input": 0}

    if "{summary}" in template_content and "{question}" in template_content:
        split_template = template_content.split("{summary}")
        length_summary["template"] += get_encoded_length(split_template[0].strip())
        output_spans.append(("template", split_template[0].strip()))

        second_half_split = split_template[1].split("{question}")
        length_summary["background"] += get_encoded_length(summary)
        output_spans.append(("background", summary))
        length_summary["template"] += get_encoded_length(second_half_split[0].strip())
        output_spans.append(("template", second_half_split[0].strip()))
        length_summary["user_input"] += get_encoded_length(question)
        output_spans.append(("user_input", question))
        
    elif "{summary}" in template_content:
        split_template = template_content.split("{summary}")
        length_summary["template"] += get_encoded_length(split_template[0].strip())
        output_spans.append(("template", split_template[0].strip()))
        length_summary["background"] += get_encoded_length(summary)
        output_spans.append(("background", summary))
    elif "{question}" in template_content:
        split_template = template_content.split("{question}")
        length_summary["template"] += get_encoded_length(split_template[0].strip())
        output_spans.append(("template", split_template[0].strip()))
        length_summary["user_input"] += get_encoded_length(question)
        output_spans.append(("user_input", question))
    else:
        length_summary["user_input"] += get_encoded_length(question)
        output_spans.append(("user_input", question))

    length_summary["total"] = sum(length_summary.values())

    return output_spans, length_summary

def format_token_count(token_count):
    summary_strs = ["**Token Count Summary**"]
    for key, value in token_count.items():
        summary_strs.append(f"{key.capitalize()}: {value}")
    return ', '.join(summary_strs)

def generate_token_report(question, summary, generation_template):
    token_count = {}
    if(summary != ""):
        template_file = get_matching_file_path(generation_template)
        if(template_file == ""):
            print(f"No template file found for {generation_template}")
            return ""
        template_content = read_file_to_string(template_file)
        [output_spans, token_count] = tag_prompt_elements(template_content, summary, question)
    else:
        output_spans = [("user_input", question)]
        #token_count = {"total" : 0}
        token_count["total"] = get_encoded_length(question)
    
    return token_count, output_spans    

def clear_content(string, clear_pad_content_enabled):
    if(clear_pad_content_enabled):
        return ""
    else:
        return string

def formatted_outputs(reply, prompt_analysis, token_count):
    return reply, prompt_analysis, format_token_count(token_count)

