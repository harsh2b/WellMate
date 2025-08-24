# ---- Build Stage ----
FROM python:3.13-slim as builder

# Set working directory
WORKDIR /app

# Install build dependencies
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Pre-download the model to the cache
ENV HUGGINGFACE_HUB_CACHE=/app/hf_cache
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"


# ---- Final Stage ----
FROM python:3.13-slim

# Set working directory
WORKDIR /app

# Create a non-root user
RUN addgroup --system appgroup && adduser --system --ingroup appgroup appuser

# Copy python dependencies and executables from builder stage
COPY --from=builder /usr/local/lib/python3.13/site-packages /usr/local/lib/python3.13/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy the downloaded model from the builder stage
ENV HUGGINGFACE_HUB_CACHE=/app/hf_cache
COPY --from=builder /app/hf_cache /app/hf_cache

# Copy application code
COPY . .

# Set ownership and permissions
RUN chown -R appuser:appgroup /app

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8000

# Set command to run the app
# Using 2 workers as a balance between performance and memory usage.
CMD ["gunicorn", "-w", "2", "-k", "uvicorn.workers.UvicornWorker", "main:app", "--bind", "0.0.0.0:8000"]
