from pathlib import Path
import os, shutil
src=Path(__file__).parent/'entry.png'
out=Path(os.environ.get('MAKEFUN_OUTPUT_DIR','/output'))
if not os.environ.get('MAKEFUN_OUTPUT_DIR') and not Path('/output').exists(): out=Path(__file__).parent/'out'
out.mkdir(parents=True,exist_ok=True)
shutil.copyfile(src,out/'entry.png')
