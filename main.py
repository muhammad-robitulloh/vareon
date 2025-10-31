# main.py
import os
import subprocess
import sys

def main():
    # Path ke file run.py relatif terhadap root proyek
    run_script = os.path.join("server-python", "run.py")

    # Pastikan file run.py ada
    if not os.path.exists(run_script):
        sys.exit("Error: server-python/run.py tidak ditemukan.")

    # Muat .env jika ada (optional, untuk local dev)
    env_path = os.path.join("server-python", ".env")
    if os.path.exists(env_path):
        print("[INFO] Memuat variabel lingkungan dari server-python/.env")
        with open(env_path) as f:
            for line in f:
                if line.strip() and not line.startswith("#"):
                    key, _, value = line.strip().partition("=")
                    os.environ[key] = value

    # Jalankan perintah Python dengan argumen
    cmd = [sys.executable, run_script, "--dev", "--with-frontend"]

    print("[INFO] Menjalankan:", " ".join(cmd))
    process = subprocess.Popen(cmd)

    # Tunggu proses selesai
    process.wait()

if __name__ == "__main__":
    main()
