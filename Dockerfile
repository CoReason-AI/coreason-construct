FROM python:3.12-slim

ENV TIKTOKEN_CACHE_DIR=/tmp/tiktoken_cache
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Create a non-root user
RUN useradd -m appuser

# Copy project files
COPY pyproject.toml README.md ./
COPY src ./src

# Install dependencies and the package
RUN pip install --no-cache-dir .

# Create tiktoken cache directory and set permissions
RUN mkdir -p $TIKTOKEN_CACHE_DIR && \
    chown -R appuser:appuser $TIKTOKEN_CACHE_DIR

# Switch to non-root user
USER appuser

# Expose the port
EXPOSE 8000

# Start the server
CMD ["uvicorn", "coreason_construct.server:app", "--host", "0.0.0.0", "--port", "8000"]
