import gradio as gr
import pickle
import modules.shared as shared
from modules.extensions import apply_extensions
from modules.text_generation import encode, get_max_prompt_length
from modules.text_generation import generate_reply
from modules.text_generation import generate_reply_wrapper
from modules.text_generation import stop_everything_event
from modules.ui import list_interface_input_elements
from modules.ui import gather_interface_values
from modules import shared,ui
from modules.html_generator import generate_basic_html


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

def copycontent(string):
    return string

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

def summarisecontent(content):
    instruction = f"Summarise the following story: \n\n********\n\n{content}\n\n********\n\nSummary:\n\n"
    # return instruction

    outputcontent = ""

    for result in generate_reply_wrapper(instruction, default_req_params):
        outputcontent += result[0]

    outputcontent = outputcontent.replace(instruction, "")

    print(f"outputcontent: {outputcontent}")
    return outputcontent


    

def ui():
    #input_elements = list_interface_input_elements(chat=False)
    #interface_state = gr.State({k: None for k in input_elements})

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

    selectStateA = gr.State('selectA')

    input_paramsA = [text_boxA,shared.gradio['interface_state'],selectStateA]
    output_paramsA =[text_boxA, htmlA]

    
    generate_btn.click(gather_interface_values, [shared.gradio[k] for k in shared.input_elements], shared.gradio['interface_state']).then(
        generate_reply_wrapper, inputs=input_paramsA, outputs=output_paramsA, show_progress=False)

    stop_btnA.click(stop_everything_event, None, None, queue=False)

    processChapter_btn.click(copycontent, text_boxA, text_box_CompiledStory )
    processChapter_btn.click(summarisecontent, text_boxA, text_box_StorySummary )
