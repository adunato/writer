import gradio as gr
import pickle
import modules.shared as shared
from modules.extensions import apply_extensions
from modules.text_generation import encode, get_max_prompt_length
from modules.text_generation import generate_reply
from modules.text_generation import generate_reply_wrapper
from modules.text_generation import stop_everything_event
# from modules.ui import create_refresh_button
# from modules.ui import gather_interface_values
import modules.ui as modules_ui
from modules import shared,ui,utils
from modules.html_generator import generate_basic_html
from pathlib import Path

try:
    with open('notebook.sav', 'rb') as f:
        params = pickle.load(f)
except FileNotFoundError:
    params = {
        "display_name": "Writer",
        "is_tab": True,
        "usePR": False,
        "pUSER": 'USER:',
        "pBOT": 'ASSISTANT:',
        "selectA": [0,0]
    }

input_elements = ['max_new_tokens', 'seed', 'temperature', 'top_p', 'top_k', 'typical_p', 'epsilon_cutoff', 'eta_cutoff', 'repetition_penalty', 'encoder_repetition_penalty', 'no_repeat_ngram_size', 'min_length', 'do_sample', 'penalty_alpha', 'num_beams', 'length_penalty', 'early_stopping', 'mirostat_mode', 'mirostat_tau', 'mirostat_eta', 'add_bos_token', 'ban_eos_token', 'truncation_length', 'custom_stopping_strings', 'skip_special_tokens', 'preset_menu', 'stream', 'tfs', 'top_a']

def copycontent(new_input,existing_text,add_cr=True):
    if(add_cr):
        return existing_text+new_input+"\n\n"
    else:
        return existing_text+new_input

default_req_params = {
    'max_new_tokens': 200,
    'temperature': 0.7,
    'top_p': 0.1,
    'top_k': 40,
    'repetition_penalty': 1.18,
    'encoder_repetition_penalty': 1.0,
    'suffix': None,
    'stream': False,
    'echo': False,
    'seed': -1,
    # 'n' : default(body, 'n', 1),  # 'n' doesn't have a direct map
    'truncation_length': 2048,
    'add_bos_token': True,
    'do_sample': True,
    'typical_p': 1.0,
    'epsilon_cutoff': 0,  # In units of 1e-4
    'eta_cutoff': 0,  # In units of 1e-4
    'tfs': 1.0,
    'top_a': 0.0,
    'min_length': 0,
    'no_repeat_ngram_size': 0,
    'num_beams': 1,
    'penalty_alpha': 0.0,
    'length_penalty': 1,
    'early_stopping': False,
    'mirostat_mode': 0,
    'mirostat_tau': 5,
    'mirostat_eta': 0.1,
    'ban_eos_token': False,
    'skip_special_tokens': True,
    'custom_stopping_strings': [],
}

summarisation_parameters = {}

text_box_LatestContext = gr.Textbox(value='', elem_classes="textbox", lines=20, label = 'Latest Context', info='This is the last context sent to the LLM as input for generation.')

def summarise_content(content, summarisation_template, state):
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

def add_summarised_content(content, text_box, summarisation_template, state, summarisation_enabled, replace=False, add_cr=True):
    if(summarisation_enabled == False):
        return ""
    summarised_content = summarise_content(content, summarisation_template, state)
    if(replace):
        text_box = summarised_content
    else:
        text_box += summarised_content
    if(add_cr):
        text_box+="\n\n"
    return text_box

def clear_content(string, clear_pad_content_enabled):
    if(clear_pad_content_enabled):
        return ""
    else:
        return string

def formatted_outputs(reply, prompt):
    return reply, generate_basic_html(reply), prompt

def tag_prompt_elements(template_content, summary, question):
    output_spans = []
    
    if "{summary}" in template_content and "{question}" in template_content:
        split_template = template_content.split("{summary}")
        output_spans.append(("template", split_template[0].strip()))

        second_half_split = split_template[1].split("{question}")
        output_spans.append(("background", summary))
        output_spans.append(("template", second_half_split[0].strip()))
        output_spans.append(("user_input", question))
        
        prompt = split_template[0] + summary + second_half_split[0] + question
    elif "{summary}" in template_content:
        split_template = template_content.split("{summary}")
        output_spans.append(("template", split_template[0].strip()))
        output_spans.append(("background", summary))
        prompt = split_template[0] + summary
    elif "{question}" in template_content:
        split_template = template_content.split("{question}")
        output_spans.append(("template", split_template[0].strip()))
        output_spans.append(("user_input", question))
        prompt = split_template[0] + question
    else:
        output_spans.append(("user_input", question))
        prompt = question

    return output_spans

def generate_reply_wrapper_enriched(question, state, selectState, summary, generation_template, eos_token=None, stopping_strings=None):
    if(summary != ""):
        template_file = get_matching_file_path(generation_template)
        if(template_file == ""):
            print(f"No template file found for {generation_template}")
            return ""
        template_content = read_file_to_string(template_file)
        output_spans = tag_prompt_elements(template_content, summary, question)
        prompt = read_file_to_string(template_file)
        prompt = prompt.replace("{summary}", summary)
        prompt = prompt.replace("{question}", question)        
    else:
        prompt = question
        output_spans = [("user_input", question)]
    # print(f"prompt: {prompt}")
    for reply in generate_reply(prompt, state, eos_token, stopping_strings, is_chat=False):
        if shared.model_type not in ['HF_seq2seq']:
            reply = question + reply
        print(f"reply: {reply}")
        yield formatted_outputs(reply, output_spans)


def copy_prompt_output(text_boxA, htmlA, prompt):
    return prompt


def get_available_templates():
    paths = (x for x in Path('extensions/writer/templates').iterdir() if x.suffix in ('.txt'))
    return ['None'] + sorted(set((k.stem for k in paths)), key=utils.natural_keys)

def gather_interface_values(*args):
    output = {}
    for i, element in enumerate(input_elements):
        output[element] = args[i]

    return output
    
def ui():
    params['selectA'] = [0,0]

    with gr.Row():
        with gr.Column():
            with gr.Row():
                with gr.Tab('Text'):
                    with gr.Row():
                        text_boxA = gr.Textbox(value='', elem_classes="textbox", lines=20, label = 'Writer Pad')
                with gr.Tab('HTML'):
                    with gr.Row():
                        htmlA = gr.HTML()
            with gr.Row():
                generate_btn = gr.Button('Generate', variant='primary', elem_classes="small-button")
                processChapter_btn = gr.Button('Process Chapter', elem_classes="small-button")
                stop_btnA = gr.Button('Stop', elem_classes="small-button")
            with gr.Row():
                with gr.Tab('Compiled Story'):
                    text_box_CompiledStory = gr.Textbox(value='', elem_classes="textbox", lines=20, label = 'Compiled Story')
                with gr.Tab('Story Summary'):
                    text_box_StorySummary = gr.Textbox(value='', elem_classes="textbox", lines=20, label = 'Story Summary')
                with gr.Tab('Latest Context'):
                    text_box_LatestContext = gr.HighlightedText(value='', elem_classes="textbox", lines=20, label = 'Latest Context', info='This is the last context sent to the LLM as input for generation.').style(color_map={"background": "red", "user_input": "green", "template": "blue"})
            with gr.Row():
                with gr.Tab('General Settings'):
                    with gr.Row():
                        summarisation_enabled_checkbox = gr.Checkbox(value=True, label='Enable auto sumarisation', info='Enables auto sumarisation when chapter is processed')
                        clear_pad_content_enabled_checkbox = gr.Checkbox(value=True, label='Clear current content', info='Content from writer pad is cleared when chapter is processed')
                    with gr.Row():
                        summarisation_template_dropdown = gr.Dropdown(choices=get_available_templates(), label='Summarisation Template', elem_id='character-menu', info='Used to summarise the story text.', value='summarisation')
                        modules_ui.create_refresh_button(summarisation_template_dropdown, lambda: None, lambda: {'choices': get_available_templates()}, 'refresh-button')
                        generation_template_dropdown = gr.Dropdown(choices=get_available_templates(), label='Generation Template', elem_id='character-menu', info='Used to generate the story.', value='generation')
                        modules_ui.create_refresh_button(generation_template_dropdown, lambda: None, lambda: {'choices': get_available_templates()}, 'refresh-button')
                with gr.Tab('Summarisation parameters'):
                    with gr.Box():
                        gr.Markdown('Summarisation parameters')
                        with gr.Row():
                            with gr.Column():
                                summarisation_parameters['temperature'] = gr.Slider(0.01, 1.99, value=default_req_params['temperature'], step=0.01, label='temperature', info='Primary factor to control randomness of outputs. 0 = deterministic (only the most likely token is used). Higher value = more randomness.')
                                summarisation_parameters['top_p'] = gr.Slider(0.0, 1.0, value=default_req_params['top_p'], step=0.01, label='top_p', info='If not set to 1, select tokens with probabilities adding up to less than this number. Higher value = higher range of possible random results.')
                                summarisation_parameters['top_k'] = gr.Slider(0, 200, value=default_req_params['top_k'], step=1, label='top_k', info='Similar to top_p, but select instead only the top_k most likely tokens. Higher value = higher range of possible random results.')
                                summarisation_parameters['typical_p'] = gr.Slider(0.0, 1.0, value=default_req_params['typical_p'], step=0.01, label='typical_p', info='If not set to 1, select only tokens that are at least this much more likely to appear than random tokens, given the prior text.')
                                summarisation_parameters['epsilon_cutoff'] = gr.Slider(0, 9, value=default_req_params['epsilon_cutoff'], step=0.01, label='epsilon_cutoff', info='In units of 1e-4; a reasonable value is 3. This sets a probability floor below which tokens are excluded from being sampled. Should be used with top_p, top_k, and eta_cutoff set to 0.')
                                summarisation_parameters['eta_cutoff'] = gr.Slider(0, 20, value=default_req_params['eta_cutoff'], step=0.01, label='eta_cutoff', info='In units of 1e-4; a reasonable value is 3. Should be used with top_p, top_k, and epsilon_cutoff set to 0.')
                                summarisation_parameters['tfs'] = gr.Slider(0.0, 1.0, value=default_req_params['tfs'], step=0.01, label='tfs')
                                summarisation_parameters['top_a'] = gr.Slider(0.0, 1.0, value=default_req_params['top_a'], step=0.01, label='top_a')
                                summarisation_parameters['max_new_tokens'] = gr.Slider(minimum=shared.settings['max_new_tokens_min'], maximum=shared.settings['max_new_tokens_max'], step=1, label='max_new_tokens', value=default_req_params['max_new_tokens'])
                                summarisation_parameters['repetition_penalty'] = gr.Slider(1.0, 1.5, value=default_req_params['repetition_penalty'], step=0.01, label='repetition_penalty', info='Exponential penalty factor for repeating prior tokens. 1 means no penalty, higher value = less repetition, lower value = more repetition.')
                                summarisation_parameters['encoder_repetition_penalty'] = gr.Slider(0.8, 1.5, value=default_req_params['encoder_repetition_penalty'], step=0.01, label='encoder_repetition_penalty', info='Also known as the "Hallucinations filter". Used to penalize tokens that are *not* in the prior text. Higher value = more likely to stay in context, lower value = more likely to diverge.')
                                summarisation_parameters['no_repeat_ngram_size'] = gr.Slider(0, 20, step=1, value=default_req_params['no_repeat_ngram_size'], label='no_repeat_ngram_size', info='If not set to 0, specifies the length of token sets that are completely blocked from repeating at all. Higher values = blocks larger phrases, lower values = blocks words or letters from repeating. Only 0 or high values are a good idea in most cases.')
                                summarisation_parameters['min_length'] = gr.Slider(0, 2000, step=1, value=default_req_params['min_length'], label='min_length', info='Minimum generation length in tokens.')
                                summarisation_parameters['do_sample'] = gr.Checkbox(value=default_req_params['do_sample'], label='do_sample')

                            with gr.Column():
                                summarisation_parameters['preset_menu'] = gr.Dropdown(choices=utils.get_available_presets(), value=utils.get_available_presets()[0] if not shared.args.flexgen else 'Naive', label='Generation parameters preset')
                                summarisation_parameters['seed'] = gr.Number(value=default_req_params['seed'], label='Seed (-1 for random)')
                                summarisation_parameters['penalty_alpha'] = gr.Slider(0, 5, value=default_req_params['penalty_alpha'], label='penalty_alpha', info='Contrastive Search is enabled by setting this to greater than zero and unchecking "do_sample". It should be used with a low value of top_k, for instance, top_k = 4.')
                                summarisation_parameters['stream'] = gr.Checkbox(value=default_req_params['stream'], label='Activate text streaming')
                                summarisation_parameters['num_beams'] = gr.Slider(1, 20, step=1, value=default_req_params['num_beams'], label='num_beams')
                                summarisation_parameters['length_penalty'] = gr.Slider(-5, 5, value=default_req_params['length_penalty'], label='length_penalty')
                                summarisation_parameters['early_stopping'] = gr.Checkbox(value=default_req_params['early_stopping'], label='early_stopping')
                                summarisation_parameters['mirostat_mode'] = gr.Slider(0, 2, step=1, value=default_req_params['mirostat_mode'], label='mirostat_mode')
                                summarisation_parameters['mirostat_tau'] = gr.Slider(0, 10, step=0.01, value=default_req_params['mirostat_tau'], label='mirostat_tau')
                                summarisation_parameters['mirostat_eta'] = gr.Slider(0, 1, step=0.01, value=default_req_params['mirostat_eta'], label='mirostat_eta')
                                summarisation_parameters['ban_eos_token'] = gr.Checkbox(value=default_req_params['ban_eos_token'], label='Ban the eos_token', info='Forces the model to never end the generation prematurely.')
                                summarisation_parameters['add_bos_token'] = gr.Checkbox(value=default_req_params['add_bos_token'], label='Add the bos_token to the beginning of prompts', info='Disabling this can make the replies more creative.')
                                summarisation_parameters['skip_special_tokens'] = gr.Checkbox(value=default_req_params['skip_special_tokens'], label='Skip special tokens', info='Some specific models need this unset.')
                                summarisation_parameters['custom_stopping_strings'] = gr.Textbox(lines=1, value=default_req_params["custom_stopping_strings"] or None, label='Custom stopping strings', info='In addition to the defaults. Written between "" and separated by commas. For instance: "\\nYour Assistant:", "\\nThe assistant:"')
                                summarisation_parameters['truncation_length'] = gr.Slider(value=default_req_params['truncation_length'], minimum=shared.settings['truncation_length_min'], maximum=shared.settings['truncation_length_max'], step=1, label='Truncate the prompt up to this length', info='The leftmost tokens are removed if the prompt exceeds this length. Most models require this to be at most 2048.')

    
    selectStateA = gr.State('selectA')
    # prompt = gr.Textbox(value='', elem_classes="textbox", lines=20, label = 'prompt')

    input_paramsA = [text_boxA,shared.gradio['interface_state'],selectStateA, text_box_StorySummary, generation_template_dropdown]
    output_paramsA =[text_boxA, htmlA, text_box_LatestContext]

    
    generate_btn.click(modules_ui.gather_interface_values, [shared.gradio[k] for k in shared.input_elements], shared.gradio['interface_state']).then(
        fn=generate_reply_wrapper_enriched, inputs=input_paramsA, outputs=output_paramsA, show_progress=False).then(fn=copy_prompt_output, inputs=output_paramsA, outputs=text_box_LatestContext)

    stop_btnA.click(stop_everything_event, None, None, queue=False)

    processChapter_btn.click(fn=copycontent, inputs=[text_boxA,text_box_CompiledStory], outputs=text_box_CompiledStory ).then(fn=gather_interface_values, inputs=[summarisation_parameters[k] for k in input_elements], outputs=shared.gradio['interface_state']).then(fn=add_summarised_content, inputs=[text_boxA, text_box_StorySummary, summarisation_template_dropdown, shared.gradio['interface_state'], summarisation_enabled_checkbox], outputs=text_box_StorySummary).then(fn=clear_content, inputs=[text_boxA, clear_pad_content_enabled_checkbox], outputs=text_boxA)

