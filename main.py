# main.py
import os
import subprocess
import sys

def main():
    # Path ke file run.py relatif terhadap root proyek
    run_script = os.path.join("server_python", "run.py")
    if not os.path.exists(run_script):
        sys.exit("Error: server_python/run.py tidak ditemukan.")
    env_path = os.path.join("server_python", ".env")
    if os.path.exists(env_path):
        print("[INFO] Memuat variabel lingkungan dari server_python/.env")
        with open(env_path) as f:
            for line in f:
                if line.strip() and not line.startswith("#"):
                    key, _, value = line.strip().partition("=")
                    os.environ[key] = value

    # Jalankan perintah Python dengan argumen
    cmd = [sys.executable, run_script, "--dev"]

    print("[INFO] Menjalankan:", " ".join(cmd))
    process = subprocess.Popen(cmd)

    # Tunggu proses selesai
    process.wait()

if __name__ == "__main__":
    main()
