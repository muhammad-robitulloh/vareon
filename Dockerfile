# Gunakan base image Python
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Salin seluruh proyek
COPY . .

# Install dependencies
RUN pip install --no-cache-dir -r server-python/requirements.txt

# Expose port Railway (otomatis diisi oleh env $PORT)

# Jalankan server Python
CMD ["python", "server-python/run.py", "--dev", "--with-frontend"]
