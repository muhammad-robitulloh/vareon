# ==========================
# 🧱 1️⃣ Base Image Python
# ==========================
FROM python:3.10-slim AS base

# Install Node.js dan npm (untuk frontend)
RUN apt-get update && apt-get install -y curl && \
    curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
    apt-get install -y nodejs && \
    npm install -g npm@latest && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Salin semua file proyek
COPY . .

# ==========================
# 🐍 2️⃣ Backend Dependencies
# ==========================
FROM base AS backend
WORKDIR /app
RUN pip install --no-cache-dir -r server-python/requirements.txt

# ==========================
# ⚛️ 3️⃣ Frontend Build
# ==========================
FROM backend AS frontend
WORKDIR /app/ai_web_dashboard/frontend

# Jalankan instalasi dependensi & build React
RUN if [ -f package.json ]; then \
      npm install && \
      npm run build; \
    fi

# ==========================
# 🚀 4️⃣ Final Runtime Image
# ==========================
FROM python:3.10-slim

# Copy hasil backend dan frontend build dari tahap sebelumnya
WORKDIR /app
COPY --from=frontend /app /app

# Install dependencies Python untuk runtime
RUN pip install --no-cache-dir -r server-python/requirements.txt

# Expose port (Railway otomatis isi $PORT)
EXPOSE 5000

# Set working directory ke backend
WORKDIR /app/server-python

# Jalankan server FastAPI via Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "5000"]
