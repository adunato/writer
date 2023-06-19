from pathlib import Path
from datetime import datetime
import json
import yaml

def save_session(writer_text_box, summary_text_box, compiled_story_text_box,summarisation_enabled_checkbox,clear_pad_content_enabled_checkbox,collate_story_enabled_checkbox,use_langchain_summarisation,chapter_separator_textbox,summarisation_template_dropdown, generation_template_dropdown, timestamp=False):
    if timestamp:
        fname = f"session_{datetime.now().strftime('%Y%m%d-%H%M%S')}.json"
    else:
        fname = f"session_persistent.json"

    if not Path('logs').exists():
        Path('logs').mkdir()

    with open(Path(f'logs/{fname}'), 'w', encoding='utf-8') as f:
        f.write(json.dumps({'writer_text_box': writer_text_box, 
                            'summary_text_box' : summary_text_box, 
                            'compiled_story_text_box' : compiled_story_text_box, 
                            'summarisation_enabled_checkbox' : summarisation_enabled_checkbox,
                            'clear_pad_content_enabled_checkbox' : clear_pad_content_enabled_checkbox,
                            'collate_story_enabled_checkbox' : collate_story_enabled_checkbox,
                            'use_langchain_summarisation' : use_langchain_summarisation,
                            'chapter_separator_textbox' : chapter_separator_textbox,
                            'summarisation_template_dropdown' : summarisation_template_dropdown,
                            'generation_template_dropdown' : generation_template_dropdown
                            }, indent=2))

    return Path(f'logs/{fname}')


def load_session(file):
    file = file.decode('utf-8')
    j = json.loads(file)
    if 'writer_text_box' in j:
        writer_text_box = j['writer_text_box']
    if 'summary_text_box' in j:
        summary_text_box = j['summary_text_box']
    if 'compiled_story_text_box' in j:
        compiled_story_text_box = j['compiled_story_text_box']
    if 'summarisation_enabled_checkbox' in j:
        summarisation_enabled_checkbox = j['summarisation_enabled_checkbox']
    if 'clear_pad_content_enabled_checkbox' in j:
        clear_pad_content_enabled_checkbox = j['clear_pad_content_enabled_checkbox']
    if 'collate_story_enabled_checkbox' in j:
        collate_story_enabled_checkbox = j['collate_story_enabled_checkbox']
    if 'use_langchain_summarisation' in j:
        use_langchain_summarisation = j['use_langchain_summarisation']
    if 'chapter_separator_textbox' in j:
        chapter_separator_textbox = j['chapter_separator_textbox']
    if 'summarisation_template_dropdown' in j:
        summarisation_template_dropdown = j['summarisation_template_dropdown']
    if 'generation_template_dropdown' in j:
        generation_template_dropdown = j['generation_template_dropdown']
    
    return writer_text_box, summary_text_box, compiled_story_text_box,summarisation_enabled_checkbox,clear_pad_content_enabled_checkbox,collate_story_enabled_checkbox,use_langchain_summarisation,chapter_separator_textbox, summarisation_template_dropdown, generation_template_dropdown

def load_preset_values(preset_menu, state, return_dict=False):
    generate_params = {
        'do_sample': True,
        'temperature': 1,
        'top_p': 1,
        'typical_p': 1,
        'epsilon_cutoff': 0,
        'eta_cutoff': 0,
        'tfs': 1,
        'top_a': 0,
        'repetition_penalty': 1,
        'encoder_repetition_penalty': 1,
        'top_k': 0,
        'num_beams': 1,
        'penalty_alpha': 0,
        'min_length': 0,
        'length_penalty': 1,
        'no_repeat_ngram_size': 0,
        'early_stopping': False,
        'mirostat_mode': 0,
        'mirostat_tau': 5.0,
        'mirostat_eta': 0.1,
    }

    with open(Path(f'presets/{preset_menu}.yaml'), 'r') as infile:
        print(f"infile: {infile}")
        preset = yaml.safe_load(infile)
        print(f"preset: {preset}")

    for k in preset:
        print(f"Updating param {k}: from {generate_params[k]} to {preset[k]}")
        generate_params[k] = preset[k]

    generate_params['temperature'] = min(1.99, generate_params['temperature'])
    if return_dict:
        return generate_params
    else:
        state.update(generate_params)
        print(f"state: {state}")
        print(f"generate_params: {generate_params}")
        return state, *[generate_params[k] for k in ['do_sample', 'temperature', 'top_p', 'typical_p', 'epsilon_cutoff', 'eta_cutoff', 'repetition_penalty', 'encoder_repetition_penalty', 'top_k', 'min_length', 'no_repeat_ngram_size', 'num_beams', 'penalty_alpha', 'length_penalty', 'early_stopping', 'mirostat_mode', 'mirostat_tau', 'mirostat_eta', 'tfs', 'top_a']]
    

def save_compiled_file(compiled_story_text, file_mode, timestamp=False):
    if timestamp:
        fname = f"compiled_story_{datetime.now().strftime('%Y%m%d-%H%M%S')}.{file_mode}"
    else:
        fname = f"compiled_story_persistent.{file_mode}"

    if not Path('logs').exists():
        Path('logs').mkdir()

    with open(Path(f'logs/{fname}'), 'w', encoding='utf-8') as f:
        f.write(compiled_story_text)

    return Path(f'logs/{fname}')
