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
from .writer_ui import generate_ui

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

text_box_LatestContext = gr.Textbox(value='', elem_classes="textbox", lines=20, label = 'Latest Context', info='This is the last context sent to the LLM as input for generation.')
    
def ui():
    generate_ui()
    
    last_input = gr.State('last_input')
    summarisation_parameters['interface_state'] = shared.gradio['interface_state']

    file_mode_txt = gr.State('txt')
    file_mode_html = gr.State('html')
    file_mode_markdown = gr.State('markdown')

    generating_text_str = gr.State('ℹ Generating text')
    processing_chapter_str = gr.State('ℹ Processing Chapter')
    chapter_processed_successfully_str = gr.State('✔ Chapter Processed Successfully')

    generation_input_params = [writer_ui["writer_pad_textbox"],shared.gradio['interface_state'], writer_ui["story_summary_textbox"], writer_ui["generation_template_dropdown"]]
    last_input_params = [last_input,shared.gradio['interface_state'], writer_ui["story_summary_textbox"], writer_ui["generation_template_dropdown"]]
    generation_output_params =[writer_ui["writer_pad_textbox"], writer_ui["latest_context_textbox"], writer_ui["token_summary_label1"]]

    writer_ui["generate_btn"].click(copy_string, generating_text_str, writer_ui["token_summary_label1"]).then(fn = modules_ui.gather_interface_values, inputs= [shared.gradio[k] for k in shared.input_elements], outputs = shared.gradio['interface_state']).then(
        copy_string, writer_ui["writer_pad_textbox"], last_input).then(
        fn=generate_reply_wrapper_enriched, inputs=generation_input_params, outputs=generation_output_params, show_progress=False).then(
        fn=copy_prompt_analysis_output, inputs=generation_output_params, outputs=writer_ui["latest_context_textbox"]).then(
        fn = generate_basic_html, inputs = writer_ui["writer_pad_textbox"], outputs = writer_ui["writer_pad_html"]).then(
        fn = convert_to_markdown, inputs = writer_ui["writer_pad_textbox"], outputs = writer_ui["writer_pad_markdown"]).then(
        fn = copy_string, inputs = writer_ui["token_summary_label1"], outputs = writer_ui["token_summary_label2"])
    
    writer_ui["writer_pad_textbox"].submit(copy_string, generating_text_str, writer_ui["token_summary_label1"]).then(fn = modules_ui.gather_interface_values, inputs= [shared.gradio[k] for k in shared.input_elements], outputs = shared.gradio['interface_state']).then(
        copy_string, writer_ui["writer_pad_textbox"], last_input).then(
        fn=generate_reply_wrapper_enriched, inputs=generation_input_params, outputs=generation_output_params, show_progress=False).then(
        fn=copy_prompt_analysis_output, inputs=generation_output_params, outputs=writer_ui["latest_context_textbox"]).then(
        fn = generate_basic_html, inputs = writer_ui["writer_pad_textbox"], outputs = writer_ui["writer_pad_html"]).then(
        fn = convert_to_markdown, inputs = writer_ui["writer_pad_textbox"], outputs = writer_ui["writer_pad_markdown"]).then(
        fn = copy_string, inputs = writer_ui["token_summary_label1"], outputs = writer_ui["token_summary_label2"])
    
    #TODO Add an instruction panel
    
    writer_ui["regenerate_btn"].click(fn = modules_ui.gather_interface_values, inputs= [shared.gradio[k] for k in shared.input_elements], outputs = shared.gradio['interface_state']).then(
        fn=generate_reply_wrapper_enriched, inputs=last_input_params, outputs=generation_output_params, show_progress=False).then(
        fn=copy_prompt_analysis_output, inputs=generation_output_params, outputs=writer_ui["latest_context_textbox"]).then(
        fn = generate_basic_html, inputs = writer_ui["writer_pad_textbox"], outputs = writer_ui["writer_pad_html"]).then(
        fn = convert_to_markdown, inputs = writer_ui["writer_pad_textbox"], outputs = writer_ui["writer_pad_markdown"]).then(
        fn = copy_string, inputs = writer_ui["token_summary_label1"], outputs = writer_ui["token_summary_label2"])

    writer_ui["stop_btn"].click(stop_everything_event, None, None, queue=False)

    writer_ui["processChapter_btn"].click(copy_string, processing_chapter_str, writer_ui["token_summary_label1"]).then(fn=copycontent, inputs=[writer_ui["collate_story_enabled_checkbox"], writer_ui["writer_pad_textbox"], writer_ui["compiled_story_textbox"], writer_ui["chapter_separator_textbox"]], outputs=writer_ui["compiled_story_textbox"] ).then(
        fn=gather_interface_values, inputs=[summarisation_parameters[k] for k in input_elements], outputs=shared.gradio['interface_state']).then(
        fn=add_summarised_content, inputs=[writer_ui["writer_pad_textbox"], writer_ui["story_summary_textbox"], writer_ui["summarisation_template_dropdown"], shared.gradio['interface_state'], writer_ui["summarisation_enabled_checkbox"]], outputs=writer_ui["story_summary_textbox"]).then(
        fn=clear_content, inputs=[writer_ui["writer_pad_textbox"], writer_ui["clear_pad_content_enabled_checkbox"]], outputs=writer_ui["writer_pad_textbox"]).then(
        fn = generate_basic_html, inputs = writer_ui["compiled_story_textbox"], outputs = writer_ui["compiled_story_html"]).then(
        fn = convert_to_markdown, inputs = writer_ui["compiled_story_textbox"], outputs = writer_ui["compiled_story_markdown"]).then(
        copy_string, chapter_processed_successfully_str, writer_ui["token_summary_label1"])
    
    summarisation_parameters['preset_menu'].change(load_preset_values, [summarisation_parameters[k] for k in ['preset_menu', 'interface_state']], [summarisation_parameters[k] for k in ['interface_state','do_sample', 'temperature', 'top_p', 'typical_p', 'epsilon_cutoff', 'eta_cutoff', 'repetition_penalty', 'encoder_repetition_penalty', 'top_k', 'min_length', 'no_repeat_ngram_size', 'num_beams', 'penalty_alpha', 'length_penalty', 'early_stopping', 'mirostat_mode', 'mirostat_tau', 'mirostat_eta', 'tfs', 'top_a']])

    writer_ui["upload_session_file"].upload(load_session, writer_ui["upload_session_file"],[writer_ui["writer_pad_textbox"], writer_ui["story_summary_textbox"], writer_ui["compiled_story_textbox"]]).then(
        fn = generate_basic_html, inputs = writer_ui["writer_pad_textbox"], outputs = writer_ui["writer_pad_html"]).then(
        fn = convert_to_markdown, inputs = writer_ui["writer_pad_textbox"], outputs = writer_ui["writer_pad_markdown"]).then(
        fn = generate_basic_html, inputs = writer_ui["compiled_story_textbox"], outputs = writer_ui["compiled_story_html"]).then(
        fn = convert_to_markdown, inputs = writer_ui["compiled_story_textbox"], outputs = writer_ui["compiled_story_markdown"])
    
    writer_ui["download_session_file_button"].click(fn = save_session, inputs = [writer_ui["writer_pad_textbox"], writer_ui["story_summary_textbox"], writer_ui["compiled_story_textbox"]], outputs = writer_ui["download_session_file"])

    writer_ui["download_compiled_text_file_button"].click(fn = save_compiled_file, inputs = [writer_ui["compiled_story_textbox"], file_mode_txt], outputs = writer_ui["download_compiled_text_file"])

    writer_ui["download_compiled_html_file_button"].click(fn = save_compiled_file, inputs = [writer_ui["compiled_story_html"], file_mode_html], outputs = writer_ui["download_compiled_html_file"])

    writer_ui["download_compiled_markdown_file_button"].click(fn = save_compiled_file, inputs = [writer_ui["compiled_story_markdown"], file_mode_markdown], outputs = writer_ui["download_compiled_markdown_file"])