from pathlib import Path
import yaml
ROOT = Path(__file__).resolve().parents[1]

def load_yaml_files(path: Path):
    out=[]
    for p in sorted(path.glob('*.yaml')):
        data=yaml.safe_load(p.read_text(encoding='utf-8')) or []
        if isinstance(data, list): out.extend(data)
        else: out.append(data)
    return out
