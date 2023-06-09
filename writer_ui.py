import gradio as gr
from modules import shared, utils
import modules.ui as modules_ui
from modules.html_generator import generate_basic_html, convert_to_markdown
from modules.text_generation import stop_everything_event
from .writer_params import writer_ui_elements, summarisation_parameters, default_req_params, input_elements, writer_ui_general_settings
from .writer_utils import get_available_templates, copy_string, copy_prompt_analysis_output, gather_interface_values, copycontent, copy_args
from .writer_prompt import generate_reply_wrapper_enriched
from .writer_io import save_compiled_file, load_preset_values, load_session, save_session
from .writer_summarise import add_summarised_content
from .writer_format_utils import clear_content

def generate_gradio_ui():
    with gr.Row():
        with gr.Column():
            with gr.Row():
                with gr.Tab('Text'):
                    with gr.Row():
                        writer_ui_elements["writer_pad_textbox"] = gr.Textbox(value='', elem_classes="textbox", lines=20, label = 'Writer Pad')
                with gr.Tab('HTML'):
                    with gr.Row():
                        writer_ui_elements["writer_pad_html"] = gr.HTML()
                with gr.Tab('Markdown'):
                    with gr.Row():
                        writer_ui_elements["writer_pad_markdown"] = gr.Markdown()
            with gr.Row():
                writer_ui_elements["generate_btn"] = gr.Button('Generate', variant='primary', elem_classes="small-button")
                writer_ui_elements["regenerate_btn"] = gr.Button('Regenerate', elem_classes="small-button")
                writer_ui_elements["processChapter_btn"] = gr.Button('Process Chapter', elem_classes="small-button")
                writer_ui_elements["stop_btn"] = gr.Button('Stop', elem_classes="small-button")
            with gr.Row():
                writer_ui_elements["token_summary_label1"] = gr.Markdown(value = '')
            with gr.Accordion('Session', open=False):
                with gr.Row():
                    with gr.Column():
                        gr.Markdown('### Upload Session')
                        writer_ui_elements["upload_session_file"] = gr.File(type='binary', file_types=['.json'])
                    with gr.Column():
                        gr.Markdown('### Download Session')
                        writer_ui_elements["download_session_file"] = gr.File()
                        writer_ui_elements["download_session_file_button"] = gr.Button(value='Click me')
            with gr.Accordion('Compiled Story', open=True):
                with gr.Row():
                    with gr.Tab('Text'):
                        writer_ui_elements["compiled_story_textbox"] = gr.Textbox(value='', elem_classes="textbox", lines=20, label = 'Compiled Story')
                    with gr.Tab('HTML'):
                        writer_ui_elements["compiled_story_html"] = gr.HTML(value='', label = 'Compiled Story')
                    with gr.Tab('Markdown'):
                        writer_ui_elements["compiled_story_markdown"] = gr.Markdown(value='', label = 'Compiled Story')
                with gr.Accordion('Download Compiled Story', open=False):
                    with gr.Row():
                        with gr.Column():
                            gr.Markdown('### Download Compiled Story (txt)')
                            writer_ui_elements["download_compiled_text_file"] = gr.File()
                            writer_ui_elements["download_compiled_text_file_button"] = gr.Button(value='Click me')
                        with gr.Column():
                            gr.Markdown('### Download Compiled Story (HTML)')
                            writer_ui_elements["download_compiled_html_file"] = gr.File()
                            writer_ui_elements["download_compiled_html_file_button"] = gr.Button(value='Click me')
                        with gr.Column():
                            gr.Markdown('### Download Compiled Story (markdown)')
                            writer_ui_elements["download_compiled_markdown_file"] = gr.File()
                            writer_ui_elements["download_compiled_markdown_file_button"] = gr.Button(value='Click me')
            with gr.Accordion('Story Generation', open=False):
                with gr.Row():
                    with gr.Tab('Story Summary'):
                        writer_ui_elements["story_summary_textbox"] = gr.Textbox(value='', elem_classes="textbox", lines=20, label = 'Story Summary')
                    with gr.Tab('Latest Context'):
                        writer_ui_elements["token_summary_label2"] = gr.Markdown(value = '')
                        writer_ui_elements["latest_context_textbox"] = gr.HighlightedText(value='', label = 'Latest Context', info='This is the last context sent to the LLM as input for generation.').style(color_map={"background": "red", "user_input": "green", "template": "blue"})
            with gr.Accordion('Settings', open=False):
                with gr.Row():
                    with gr.Tab('General Settings'):
                        with gr.Row():
                            writer_ui_general_settings["summarisation_enabled_checkbox"] = gr.Checkbox(value=True, label='Enable auto sumarisation', info='Enables auto sumarisation when chapter is processed')
                            writer_ui_general_settings["clear_pad_content_enabled_checkbox"] = gr.Checkbox(value=True, label='Clear current content', info='Content from writer pad is cleared when chapter is processed')
                            writer_ui_general_settings["collate_story_enabled_checkbox"] = gr.Checkbox(value=True, label='Collate story', info='Content from writer pad is collated into the story tab')
                            writer_ui_general_settings["use_langchain_summarisation"] = gr.Checkbox(value=True, label='Enable auto sumarisation using Langchain', info='Uses Langchain instead of custom summarisation module')
                            writer_ui_general_settings["chapter_separator_textbox"] = gr.Textbox(value='\n*********\n', elem_classes="textbox", lines=1, label = 'Chapter Separator', info = 'Adds a separator after each chapter has been processed in the collated story')
                        with gr.Row():
                            writer_ui_general_settings["summarisation_template_dropdown"] = gr.Dropdown(choices=get_available_templates(), label='Summarisation Template', elem_id='character-menu', info='Used to summarise the story text.', value='summarisation')
                            modules_ui.create_refresh_button(writer_ui_general_settings["summarisation_template_dropdown"], lambda: None, lambda: {'choices': get_available_templates()}, 'refresh-button')
                            writer_ui_general_settings["generation_template_dropdown"] = gr.Dropdown(choices=get_available_templates(), label='Generation Template', elem_id='character-menu', info='Used to generate the story.', value='generation')
                            modules_ui.create_refresh_button(writer_ui_general_settings["generation_template_dropdown"], lambda: None, lambda: {'choices': get_available_templates()}, 'refresh-button')
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

def generate_button_callbacks():
    last_input = gr.State('last_input')
    writer_summarisation_ui_state = gr.State()

    file_mode_txt = gr.State('txt')
    file_mode_html = gr.State('html')
    file_mode_markdown = gr.State('markdown')

    generating_text_str = gr.State('ℹ Generating text')
    processing_chapter_str = gr.State('ℹ Processing Chapter')
    chapter_processed_successfully_str = gr.State('✔ Chapter Processed Successfully')

    generation_input_params = [writer_ui_elements["writer_pad_textbox"],shared.gradio['interface_state'], writer_ui_elements["story_summary_textbox"], writer_ui_general_settings["generation_template_dropdown"]]
    last_input_params = [last_input,shared.gradio['interface_state'], writer_ui_elements["story_summary_textbox"], writer_ui_general_settings["generation_template_dropdown"]]
    generation_output_params =[writer_ui_elements["writer_pad_textbox"], writer_ui_elements["latest_context_textbox"], writer_ui_elements["token_summary_label1"]]

    writer_ui_elements["generate_btn"].click(copy_string, generating_text_str, writer_ui_elements["token_summary_label1"]).then(fn = modules_ui.gather_interface_values, inputs= [shared.gradio[k] for k in shared.input_elements], outputs = shared.gradio['interface_state']).then(
        copy_string, writer_ui_elements["writer_pad_textbox"], last_input).then(
        fn=generate_reply_wrapper_enriched, inputs=generation_input_params, outputs=generation_output_params, show_progress=False).then(
        fn=copy_prompt_analysis_output, inputs=generation_output_params, outputs=writer_ui_elements["latest_context_textbox"]).then(
        fn = generate_basic_html, inputs = writer_ui_elements["writer_pad_textbox"], outputs = writer_ui_elements["writer_pad_html"]).then(
        fn = convert_to_markdown, inputs = writer_ui_elements["writer_pad_textbox"], outputs = writer_ui_elements["writer_pad_markdown"]).then(
        fn = copy_string, inputs = writer_ui_elements["token_summary_label1"], outputs = writer_ui_elements["token_summary_label2"])
    
    writer_ui_elements["writer_pad_textbox"].submit(copy_string, generating_text_str, writer_ui_elements["token_summary_label1"]).then(fn = modules_ui.gather_interface_values, inputs= [shared.gradio[k] for k in shared.input_elements], outputs = shared.gradio['interface_state']).then(
        copy_string, writer_ui_elements["writer_pad_textbox"], last_input).then(
        fn=generate_reply_wrapper_enriched, inputs=generation_input_params, outputs=generation_output_params, show_progress=False).then(
        fn=copy_prompt_analysis_output, inputs=generation_output_params, outputs=writer_ui_elements["latest_context_textbox"]).then(
        fn = generate_basic_html, inputs = writer_ui_elements["writer_pad_textbox"], outputs = writer_ui_elements["writer_pad_html"]).then(
        fn = convert_to_markdown, inputs = writer_ui_elements["writer_pad_textbox"], outputs = writer_ui_elements["writer_pad_markdown"]).then(
        fn = copy_string, inputs = writer_ui_elements["token_summary_label1"], outputs = writer_ui_elements["token_summary_label2"])
    
    #TODO Add an instruction panel
    
    writer_ui_elements["regenerate_btn"].click(fn = modules_ui.gather_interface_values, inputs= [shared.gradio[k] for k in shared.input_elements], outputs = shared.gradio['interface_state']).then(
        fn=generate_reply_wrapper_enriched, inputs=last_input_params, outputs=generation_output_params, show_progress=False).then(
        fn=copy_prompt_analysis_output, inputs=generation_output_params, outputs=writer_ui_elements["latest_context_textbox"]).then(
        fn = generate_basic_html, inputs = writer_ui_elements["writer_pad_textbox"], outputs = writer_ui_elements["writer_pad_html"]).then(
        fn = convert_to_markdown, inputs = writer_ui_elements["writer_pad_textbox"], outputs = writer_ui_elements["writer_pad_markdown"]).then(
        fn = copy_string, inputs = writer_ui_elements["token_summary_label1"], outputs = writer_ui_elements["token_summary_label2"])

    writer_ui_elements["stop_btn"].click(stop_everything_event, None, None, queue=False)

    writer_ui_elements["processChapter_btn"].click(copy_string, processing_chapter_str, writer_ui_elements["token_summary_label1"]).then(fn=copycontent, inputs=[writer_ui_general_settings["collate_story_enabled_checkbox"], writer_ui_elements["writer_pad_textbox"], writer_ui_elements["compiled_story_textbox"], writer_ui_general_settings["chapter_separator_textbox"]], outputs=writer_ui_elements["compiled_story_textbox"] ).then(
        fn=gather_interface_values, inputs=[summarisation_parameters[k] for k in input_elements], outputs=writer_summarisation_ui_state).then(
        fn=add_summarised_content, inputs=[writer_ui_elements["writer_pad_textbox"], writer_ui_elements["story_summary_textbox"], writer_ui_general_settings["summarisation_template_dropdown"], writer_ui_elements["story_summary_textbox"], writer_summarisation_ui_state, writer_ui_general_settings["use_langchain_summarisation"], writer_ui_general_settings["summarisation_enabled_checkbox"]], outputs=writer_ui_elements["story_summary_textbox"]).then(
        fn=clear_content, inputs=[writer_ui_elements["writer_pad_textbox"], writer_ui_general_settings["clear_pad_content_enabled_checkbox"]], outputs=writer_ui_elements["writer_pad_textbox"]).then(
        fn = generate_basic_html, inputs = writer_ui_elements["compiled_story_textbox"], outputs = writer_ui_elements["compiled_story_html"]).then(
        fn = convert_to_markdown, inputs = writer_ui_elements["compiled_story_textbox"], outputs = writer_ui_elements["compiled_story_markdown"]).then(
        copy_string, chapter_processed_successfully_str, writer_ui_elements["token_summary_label1"])
    
    summarisation_parameters['preset_menu'].change(fn=gather_interface_values, inputs=[summarisation_parameters[k] for k in input_elements], outputs=writer_summarisation_ui_state).then(fn=load_preset_values,inputs= [summarisation_parameters['preset_menu'], writer_summarisation_ui_state],outputs=[writer_summarisation_ui_state] + [summarisation_parameters[k] for k in ['do_sample', 'temperature', 'top_p', 'typical_p', 'epsilon_cutoff', 'eta_cutoff', 'repetition_penalty', 'encoder_repetition_penalty', 'top_k', 'min_length', 'no_repeat_ngram_size', 'num_beams', 'penalty_alpha', 'length_penalty', 'early_stopping', 'mirostat_mode', 'mirostat_tau', 'mirostat_eta', 'tfs', 'top_a']])

    writer_ui_elements["download_compiled_text_file_button"].click(fn = save_compiled_file, inputs = [writer_ui_elements["compiled_story_textbox"], file_mode_txt], outputs = writer_ui_elements["download_compiled_text_file"])

    writer_ui_elements["download_compiled_html_file_button"].click(fn = save_compiled_file, inputs = [writer_ui_elements["compiled_story_html"], file_mode_html], outputs = writer_ui_elements["download_compiled_html_file"])

    writer_ui_elements["download_compiled_markdown_file_button"].click(fn = save_compiled_file, inputs = [writer_ui_elements["compiled_story_markdown"], file_mode_markdown], outputs = writer_ui_elements["download_compiled_markdown_file"])    

    #Session serialisation

    save_elements = {}
    save_elements.update(writer_ui_elements)
    save_elements.update(writer_ui_general_settings)
    save_elements.update(summarisation_parameters)
    save_serialised_elements = save_elements

    def make_save_session():
        def save_session_cl(timestamp=False):
            print(f"save_session_cl save_params: {save_serialised_elements}")
            return save_session(save_serialised_elements, timestamp=timestamp)
        return save_session_cl

    save_session_fn = make_save_session()

    writer_ui_elements["download_session_file_button"].click(
    fn=lambda *values: save_serialised_elements.update({k: v for k, v in zip(save_serialised_elements.keys(), values)}),
    inputs=[save_elements[k] for k in save_elements.keys()],
    outputs=[]
    ).then(
         fn=save_session_fn, inputs=[], outputs=writer_ui_elements["download_session_file"])

    writer_ui_elements["upload_session_file"].upload(fn = load_session, inputs = [writer_ui_elements["upload_session_file"]], outputs = [save_elements[k] for k in save_elements.keys()])
