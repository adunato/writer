import gradio as gr
import pickle
import modules.shared as shared
from pathlib import Path
from datetime import datetime
from modules.text_generation import stop_everything_event
from modules import shared,ui,utils
import modules.ui as modules_ui
from modules.html_generator import generate_basic_html, convert_to_markdown
from .writer_utils import copycontent, copy_string, copy_prompt_analysis_output, copy_args, copy_string, get_available_templates, gather_interface_values
from .writer_params import input_elements, default_req_params, summarisation_parameters, writer_ui
from .writer_io import load_session, save_session, load_preset_values, save_compiled_file
from .writer_summarise import add_summarised_content
from .writer_format_utils import tag_prompt_elements, format_token_count, generate_token_report, formatted_outputs, clear_content
from .writer_prompt import generate_prompt, truncate_prompt, generate_reply_wrapper_enriched, get_max_prompt_tokens, truncate_tokens
from .writer_ui import generate_gradio_ui, generate_button_callbacks

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
        # "selectA": [0,0]
    }

def ui():
    generate_gradio_ui()
    generate_button_callbacks()
    
