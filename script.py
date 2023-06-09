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

def ui():
    #input_elements = list_interface_input_elements(chat=False)
    #interface_state = gr.State({k: None for k in input_elements})

    params['selectA'] = [0,0]
    params['selectB'] = [0,0]

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
                generate_btn_ProcessChapter = gr.Button('Process Chapter', variant='primary', elem_classes="small-button")
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

    # Define input and output parameters for generate_btn_ProcessChapter
    input_paramsB = [text_boxA,shared.gradio['interface_state'],selectStateA]
    output_paramsB =[text_box_CompiledStory]

    # Add click event for generate_btn_ProcessChapter
    generate_btn_ProcessChapter.click(gather_interface_values, [shared.gradio[k] for k in shared.input_elements], shared.gradio['interface_state']).then(
            generate_reply_wrapper, inputs=input_paramsB, outputs=output_paramsB, show_progress=False)

   
