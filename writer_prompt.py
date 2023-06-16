from modules.text_generation import get_encoded_length
from .writer_utils import get_matching_file_path, read_file_to_string
from .writer_format_utils import generate_token_report, formatted_outputs
from modules.text_generation import generate_reply
from modules import shared

def generate_prompt(question, summary, generation_template):
    if(summary != ""):
        template_file = get_matching_file_path(generation_template)
        if(template_file == ""):
            print(f"No template file found for {generation_template}")
            return ""
        prompt = read_file_to_string(template_file)
        prompt = prompt.replace("{summary}", summary)
        prompt = prompt.replace("{question}", question)
    else:
        prompt = question
    return prompt

def truncate_prompt(question, prompt):
    # Calculate the total number of tokens in the prompt
    total_prompt_tokens = get_encoded_length(prompt)
    print(f"total_prompt_tokens:{total_prompt_tokens}")
    # Check if the total number of tokens exceeds the maximum allowable tokens
    max_prompt_tokens = get_max_prompt_tokens()
    print(f"max_prompt_tokens:{max_prompt_tokens}")
    truncated_question = question
    if total_prompt_tokens > max_prompt_tokens:
        # If the total number of tokens is greater than the max allowable tokens,
        # truncate the question from the beginning by the excess number of tokens
        excess_tokens = total_prompt_tokens - max_prompt_tokens
        truncated_question = truncate_tokens(question, excess_tokens)
        prompt = prompt.replace(question, truncated_question) # replace old question with truncated one   
        print(f"truncated_question:{truncated_question}")
        print(f"prompt:{prompt}")
    return prompt, truncated_question

def generate_reply_wrapper_enriched(question, state, summary, generation_template, eos_token=None, stopping_strings=None):
    prompt = generate_prompt(question, summary, generation_template)
 
    prompt, truncated_question = truncate_prompt(question, prompt)

    token_count, output_spans = generate_token_report(truncated_question, summary, generation_template)

    for reply in generate_reply(prompt, state, eos_token, stopping_strings, is_chat=False):
        if shared.model_type not in ['HF_seq2seq']:
            reply = question + reply
        yield formatted_outputs(reply, output_spans, token_count)



def get_max_prompt_tokens():
    return shared.settings['max_new_tokens_max'] - shared.gradio['max_new_tokens'].value

def truncate_tokens(text, excess_tokens):
    words = text.split()
    total_tokens = get_encoded_length(text)
    
    # Estimate average tokens per word
    avg_tokens_per_word = total_tokens / len(words)
    
    # Estimate the number of words to remove
    estimated_words_to_remove = int(excess_tokens / avg_tokens_per_word)
    
    # Remove estimated number of words
    words = words[estimated_words_to_remove:]
    
    # Fine-tune by removing extra words if necessary
    while get_encoded_length(' '.join(words)) > excess_tokens:
        words = words[1:]

    return ' '.join(words)