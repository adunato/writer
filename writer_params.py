input_elements = ['max_new_tokens', 'seed', 'temperature', 'top_p', 'top_k', 'typical_p', 'epsilon_cutoff', 'eta_cutoff', 'repetition_penalty', 'encoder_repetition_penalty', 'no_repeat_ngram_size', 'min_length', 'do_sample', 'penalty_alpha', 'num_beams', 'length_penalty', 'early_stopping', 'mirostat_mode', 'mirostat_tau', 'mirostat_eta', 'add_bos_token', 'ban_eos_token', 'truncation_length', 'custom_stopping_strings', 'skip_special_tokens', 'preset_menu', 'stream', 'tfs', 'top_a']

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

writer_ui_elements = {}

writer_ui_general_settings = {}