#/bin/bash
if [ ! -d "/workspace/venv/" ]; then
    python -m venv /workspace/venv/
fi
## Activate the Python venv by default
echo 'source /workspace/venv/bin/activate' >> ~/.bashrc
## Install requirements
pip install -r /workspace/requirements.txt
cd /workspace && pnpm install