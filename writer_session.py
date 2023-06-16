from pathlib import Path
from datetime import datetime
import json

def save_session(writer_text_box, summary_text_box, compiled_story_text_box, timestamp=False):
    if timestamp:
        fname = f"session_{datetime.now().strftime('%Y%m%d-%H%M%S')}.json"
    else:
        fname = f"session_persistent.json"

    if not Path('logs').exists():
        Path('logs').mkdir()

    with open(Path(f'logs/{fname}'), 'w', encoding='utf-8') as f:
        f.write(json.dumps({'writer_text_box': writer_text_box, 'summary_text_box' : summary_text_box, 'compiled_story_text_box' : compiled_story_text_box}, indent=2))

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
    return writer_text_box, summary_text_box, compiled_story_text_box

