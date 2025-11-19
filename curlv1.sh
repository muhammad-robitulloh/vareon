#!/bin/bash

# Skrip untuk secara otomatis mengambil token otentikasi dan menggunakannya
# untuk mengirim prompt ke endpoint chat Vareon Cognisys.
#
# Prasyarat:
# 1. Server Vareon harus berjalan di http://127.0.0.1:5000.
# 2. `curl` dan `jq` harus terinstal dan ada di PATH Anda.
#
# Untuk membuat skrip ini dapat dieksekusi, jalankan:
# chmod +x curlv1.sh

# --- Konfigurasi ---
BASE_URL="http://127.0.0.1:5000"
TOKEN_ENDPOINT="$BASE_URL/api/token"
CHAT_ENDPOINT="$BASE_URL/api/cognisys/chat"

# --- Langkah 1: Dapatkan Token Otentikasi ---
echo "Mencoba mendapatkan token otentikasi dari $TOKEN_ENDPOINT..."

# Jalankan curl dan parsing respons JSON dengan jq untuk mengekstrak access_token
# Opsi -s membuat curl berjalan dalam mode senyap (tanpa progress meter)
AUTH_TOKEN=$(curl -s -X POST \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=testuser&password=testpassword" \
  "$TOKEN_ENDPOINT" | jq -r .access_token)

# --- Langkah 2: Periksa apakah Token Berhasil Didapatkan ---
if [ -z "$AUTH_TOKEN" ] || [ "$AUTH_TOKEN" == "null" ]; then
  echo "Error: Gagal mendapatkan token otentikasi. Pastikan server berjalan dan kredensial sudah benar."
  exit 1
fi

echo "Berhasil mendapatkan token otentikasi."
echo "---"

# --- Langkah 3: Kirim Prompt ke Cognisys ---
echo "Mengirim prompt orkestrasi ke $CHAT_ENDPOINT..."

# Definisikan payload JSON
JSON_PAYLOAD='{
  "prompt": "Tolong buatkan skrip python di dalam file bernama '\''test_script.py'\''. Skrip tersebut harus berisi fungsi yang menerima dua angka dan mengembalikan jumlahnya, beserta satu contoh pemanggilan fungsi tersebut."
}'

# Jalankan perintah curl utama menggunakan token yang telah didapatkan
curl -X POST "$CHAT_ENDPOINT" \
-H "Authorization: Bearer $AUTH_TOKEN" \
-H "Content-Type: application/json" \
-d "$JSON_PAYLOAD"

echo # Tambahkan baris baru untuk output terminal yang lebih bersih
