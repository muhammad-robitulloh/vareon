# Gunakan base image Python
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Salin seluruh proyek
COPY . .

# Install dependencies
RUN pip install --no-cache-dir -r server-python/requirements.txt

# Expose port Railway (otomatis diisi oleh env $PORT)
EXPOSE 5000

# Jalankan server Python
CMD ["python", "server-python/run.py", "--host", "0.0.0.0", "--port", "5000"]
