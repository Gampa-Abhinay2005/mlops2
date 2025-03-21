# Set shell mode
set shell := ["bash", "-c"]

# Define virtual environment name
venv := ".venv_gesture"

# Create virtual environment and install dependencies using uv
setup:
    # Create virtual environment
    uv venv --python=python3.11 {{venv}}  
    source .venv_gesture/bin/activate && uv pip install -r requirements.txt
    bentoml build

# Run the main Gradio application
run:
    source .venv_gesture/bin/activate && uv run gradio_ui.py  
# Clean up virtual environment
clean:
    rm -rf {{venv}}

# Display help message
help:
    @echo "Available commands:"
    @echo "  setup  - Install system dependencies, create virtual environment, and install Python packages"
    @echo "  run    - Start the Gradio application"
    @echo "  clean  - Remove virtual environment"