FROM python:3.10-slim

# Create a non-root user with UID 1000 as recommended by Hugging Face Spaces
RUN useradd -m -u 1000 user

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Set ownership to the non-root user
RUN chown -R user:user /app

# Switch to the non-root user
USER user

EXPOSE 8000

CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000"]
