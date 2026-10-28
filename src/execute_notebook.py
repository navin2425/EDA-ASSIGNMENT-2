"""
Execute notebooks/eda_churn.ipynb top-to-bottom and save with full outputs.
"""
import os
os.environ['IPYTHONDIR'] = os.path.abspath('outputs/.ipython')
os.environ['JUPYTER_DATA_DIR'] = os.path.abspath('outputs/.jupyter_data')
os.environ['JUPYTER_RUNTIME_DIR'] = os.path.abspath('outputs/.jupyter_runtime')
os.environ['JUPYTER_CONFIG_DIR'] = os.path.abspath('outputs/.jupyter_config')
os.environ['MPLCONFIGDIR'] = os.path.abspath('outputs/.matplotlib')

for d in ['outputs/.ipython', 'outputs/.jupyter_data', 'outputs/.jupyter_runtime', 'outputs/.jupyter_config', 'outputs/.matplotlib']:
    os.makedirs(d, exist_ok=True)

import nbformat
from nbclient import NotebookClient

def execute():
    nb_path = 'notebooks/eda_churn.ipynb'
    print(f"Reading {nb_path}...")
    with open(nb_path, 'r', encoding='utf-8') as f:
        nb = nbformat.read(f, as_version=4)

    client = NotebookClient(nb, timeout=300, kernel_name='python3')
    print("Executing notebook top-to-bottom...")
    client.execute()

    print(f"Saving executed notebook to {nb_path}...")
    with open(nb_path, 'w', encoding='utf-8') as f:
        nbformat.write(nb, f)
    print("Notebook executed and saved successfully with all outputs!")

if __name__ == '__main__':
    execute()
