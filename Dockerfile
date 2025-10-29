# Base image dengan Python
FROM python:3.10-slim

# Install Node.js dan npm
RUN apt-get update && apt-get install -y curl && \
    curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
    apt-get install -y nodejs && \
    npm install -g npm@latest && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy semua file ke container
COPY . .

# Install dependencies Python
RUN pip install --no-cache-dir -r server-python/requirements.txt

# Install dependencies frontend jika ada folder frontend/
WORKDIR /app/ai_web_dashboard/frontend
RUN if [ -f package.json ]; then npm install && npm run build; fi

# Kembali ke root project
WORKDIR /app

# Expose port (Railway akan isi $PORT otomatis)
EXPOSE 5000

# Jalankan backend + frontend build mode
CMD ["python", "server-python/run.py", "--dev", "--with-frontend"]
