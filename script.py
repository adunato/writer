import pickle
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
    
