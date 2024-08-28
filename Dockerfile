# Start with the Miniconda3 base image
FROM continuumio/miniconda3:latest

# Set the working directory in the container
WORKDIR /app


# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    swig \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

# Create a Conda environment and install faiss-cpu
RUN conda install -c conda-forge faiss-cpu

# Alternatively, you can use environment.yml to manage the environment (uncomment if you have environment.yml)
# RUN conda env create -f environment.yml && conda clean -afy

# Install Python dependencies via pip
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# If you have specific Python dependencies that are not in requirements.txt, you can also add them here
RUN pip install --no-cache-dir fastapi==0.112.2 \
    uvicorn==0.30.6 \
    openai==0.28.0 \
    requests==2.32.3 \
    farm-haystack[sql] \
    farm-haystack[inference] \
    python-multipart

# Copy your application code to the container
COPY . /app

# Expose the port FastAPI will run on
EXPOSE 80

# Command to run the FastAPI application
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "80"]
