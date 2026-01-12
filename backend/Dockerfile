# Base image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies (needed for llama-cpp-python and other native extensions)
RUN apt-get update && apt-get install -y gcc g++ cmake make python3-dev curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
# Copy requirements
COPY requirements.txt .

# Optimize for CPU: Install PyTorch CPU-only FIRST to avoid downloading NVIDIA CUDA binaries
# sentence-transformers depends on torch, so we must preemptively install the CPU version
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu

# Install remaining dependencies
# FORCE_CMAKE=1 ensures llama-cpp-python builds from source if needed
ENV FORCE_CMAKE=1
RUN pip install --no-cache-dir -r requirements.txt

# Download the LLM Model
# We do this during build so it's baked into the image (easier for deployment, though larger image)
# Using bartowski/Meta-Llama-3.1-8B-Instruct-GGUF as a reliable source
RUN python -c "from huggingface_hub import hf_hub_download; \
    print('Downloading Llama 3.1 8B GGUF...'); \
    hf_hub_download(repo_id='bartowski/Meta-Llama-3.1-8B-Instruct-GGUF', \
    filename='Meta-Llama-3.1-8B-Instruct-Q4_K_M.gguf', \
    local_dir='/app/backend/models')"

# Copy application code
COPY . ./backend

# Environment variables
ENV PYTHONPATH=/app
ENV MODEL_PATH=/app/backend/models/Meta-Llama-3.1-8B-Instruct-Q4_K_M.gguf

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
