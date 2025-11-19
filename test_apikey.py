import httpx
import asyncio
import json

# API key yang Anda berikan
API_KEY = "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"

# Endpoint API OpenRouter
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

# Payload minimal untuk pengujian menggunakan model yang gratis dan cepat
TEST_PAYLOAD = {
  "model": "mistralai/mistral-7b-instruct:free",
  "messages": [
    {"role": "user", "content": "This is a connection test. Respond with a single word."}
  ]
}

async def test_openrouter_key():
    """
    Menguji kunci API OpenRouter yang diberikan dengan membuat panggilan API sederhana.
    """
    print("--- Tes Kunci API OpenRouter ---")
    print(f"Menggunakan API Key (8 karakter pertama): {API_KEY[:8]}...")
    print(f"URL Target: {OPENROUTER_URL}")
    print("-" * 30)

    if not API_KEY:
        print("HASIL: GAGAL - Kunci API kosong.")
        return

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    try:
        async with httpx.AsyncClient() as client:
            print("Mengirim permintaan ke OpenRouter...")
            response = await client.post(
                OPENROUTER_URL,
                headers=headers,
                json=TEST_PAYLOAD,
                timeout=30.0
            )

            print(f"Menerima Kode Status HTTP: {response.status_code}")

            # Periksa kode status respons
            if response.status_code == 200:
                print("\nHASIL: SUKSES!")
                print("Kunci API valid dan koneksi ke OpenRouter berhasil.")
                try:
                    response_data = response.json()
                    print("\n--- Data Respons ---")
                    print(json.dumps(response_data, indent=2))
                    print("--------------------")
                except json.JSONDecodeError:
                    print("Tidak dapat mendekode respons JSON, tetapi koneksi berhasil.")
                    print(f"Respons mentah: {response.text}")

            elif response.status_code == 401:
                print("\nHASIL: GAGAL - ERROR AUTENTIKASI (401)")
                print("Kunci API ini TIDAK VALID, KEDALUWARSA, atau tidak memiliki izin untuk model yang diminta.")
                print("Mohon periksa kembali kunci yang Anda berikan.")
                print(f"Respons error mentah: {response.text}")

            else:
                print(f"\nHASIL: GAGAL - ERROR HTTP {response.status_code}")
                print("Permintaan gagal dengan kode status HTTP yang tidak terduga.")
                print(f"Respons error mentah: {response.text}")

    except httpx.RequestError as e:
        print(f"\nHASIL: GAGAL - ERROR JARINGAN")
        print("Tidak dapat terhubung ke OpenRouter. Periksa koneksi internet Anda.")
        print(f"Detail error: {e}")
    except Exception as e:
        print(f"\nHASIL: GAGAL - ERROR SKRIP YANG TIDAK TERDUGA")
        print(f"Terjadi error yang tidak terduga: {e}")

if __name__ == "__main__":
    asyncio.run(test_openrouter_key())
