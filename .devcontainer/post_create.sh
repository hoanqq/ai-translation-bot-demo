#!/bin/bash

# Define the path to your Zsh profile
zshrc_path="$HOME/.zshrc"
bashrc_path="$HOME/.bashrc"

echo "export PATH=\"$HOME/.local/bin:$PATH\"" >> "$zshrc_path"
echo "export PATH=\"$HOME/.local/bin:$PATH\"" >> "$bashrc_path"
echo "export PYTHONPATH=\"$PYTHONPATH:/workspaces/ai-translation-bot-demo/app/\"" >> "$zshrc_path"
echo "export PYTHONPATH=\"$PYTHONPATH:/workspaces/ai-translation-bot-demo/app/\"" >> "$bashrc_path"
echo "export PYTHONPATH=\"$PYTHONPATH:/workspaces/ai-translation-bot-demo/frontend/\"" >> "$zshrc_path"
echo "export PYTHONPATH=\"$PYTHONPATH:/workspaces/ai-translation-bot-demo/frontend/\"" >> "$bashrc_path"

cat "$HOME"/.zshrc
export PATH="$HOME/.local/bin:$PATH"

# install the requirements for backend
pip install --user -r requirements.txt
