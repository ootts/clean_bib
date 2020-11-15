# clean_bib
Tools to clean uncited references and convert arxiv bibtex.

# Usage
1. clone this repo.
2. install requirements using pip.
```bash
pip install -r requirements.txt
```
3. compile your latex sources and find a .aux file.
4. use this tool
```bash
python main.py --input_path INPUT_BIB_PATH --output_path OUTPUT_BIB_PATH --aux_path AUX_FILE_PATH --checkciteslua_path checkcites.lua
```
