# Set shell mode
set shell := ["bash", "-c"]

# Define virtual environment name
venv := ".venv_gesture"

# Create virtual environment and install dependencies using uv
setup:
    # Install Linux system dependencies (if needed)
    sudo apt update && sudo apt install -y ffmpeg libsm6 libxext6  
    # Create virtual environment
    uv venv --python=python3.11 {{venv}}  

    # Install dependencies using uv
    uv pip install -r requirements.txt  

# Run the main Gradio application
run:
    uv venv exec python gradio_ui.py  
# Clean up virtual environment
clean:
    rm -rf {{venv}}

# Display help message
help:
    @echo "Available commands:"
    @echo "  setup  - Install system dependencies, create virtual environment, and install Python packages"
    @echo "  run    - Start the Gradio application"
    @echo "  clean  - Remove virtual environment"
