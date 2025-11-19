import httpx
import asyncio
import json

# API key yang Anda berikan
API_KEY = "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"

# Endpoint API OpenRouter
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

# Payload LENGKAP, sama seperti yang dikirim oleh server Anda dari log
# Ini termasuk daftar tools yang besar
FULL_PAYLOAD = {
  "model": "mistralai/mistral-7b-instruct:free",
  "messages": [
    {
      "role": "user",
      "content": "Tolong buatkan skrip python di dalam file bernama 'test_script.py'. Skrip tersebut harus berisi fungsi yang menerima dua angka dan mengembalikan jumlahnya, beserta satu contoh pemanggilan fungsi tersebut."
    }
  ],
  "temperature": 0.7,
  "top_p": 1.0,
  "tools": [
    {
      "type": "function",
      "function": {
        "name": "execute_shell_command",
        "description": "Executes a simple, single-line shell command in the user's sandboxed environment and returns the output. Useful for listing files, reading file content, or quick checks. Not for complex or multi-step operations.",
        "parameters": {
          "type": "object",
          "properties": {
            "command": {
              "type": "string",
              "description": "The shell command to execute (e.g., 'ls -l', 'cat my_file.txt')."
            }
          },
          "required": ["command"]
        }
      }
    },
    {
      "type": "function",
      "function": {
        "name": "delegate_task_to_arcana",
        "description": "Delegates a complex, multi-step task to a specialized 'Arcana' agent. Use this for tasks involving coding, file editing, running tests, or complex git workflows. This is the preferred tool for any software development task.",
        "parameters": {
          "type": "object",
          "properties": {
            "task_prompt": {
              "type": "string",
              "description": "A clear, detailed, and self-contained natural language prompt describing the entire task for the Arcana agent."
            },
            "parent_job_id": {
              "type": "string",
              "description": "Optional: The ID of the parent job in Cognisys, for hierarchical tracking."
            }
          },
          "required": ["task_prompt"]
        }
      }
    },
    {
      "type": "function",
      "function": {
        "name": "git_clone_repo",
        "description": "Clones a Git repository from a given URL to a local path. Requires a GitHub Personal Access Token (PAT) for private repositories.",
        "parameters": {
          "type": "object",
          "properties": {
            "repo_url": {"type": "string"},
            "local_path": {"type": "string"},
            "pat": {"type": "string"},
            "branch": {"type": "string"}
          },
          "required": ["repo_url", "local_path"]
        }
      }
    },
    {
      "type": "function",
      "function": {
        "name": "git_get_status",
        "description": "Gets the current Git status of a repository, including current branch, dirty state, staged, unstaged, and untracked files.",
        "parameters": {
          "type": "object",
          "properties": {
            "local_path": {"type": "string"}
          },
          "required": ["local_path"]
        }
      }
    }
  ],
  "tool_choice": "auto"
}

async def test_full_payload():
    """
    Tests the full, complex payload against the OpenRouter API.
    """
    print("--- Tes Payload Lengkap ke OpenRouter ---")
    print(f"Menggunakan API Key (8 karakter pertama): {API_KEY[:8]}...")
    print("-" * 30)

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    try:
        # Set timeout to a higher value (e.g., 120 seconds) to account for complex requests
        timeout = httpx.Timeout(120.0, connect=10.0)
        async with httpx.AsyncClient(timeout=timeout) as client:
            print("Mengirim payload lengkap ke OpenRouter (ini mungkin butuh waktu)...")
            response = await client.post(
                OPENROUTER_URL,
                headers=headers,
                json=FULL_PAYLOAD
            )

            print(f"Menerima Kode Status HTTP: {response.status_code}")

            if response.status_code == 200:
                print("\n\033[92mHASIL: SUKSES!\033[0m")
                print("OpenRouter berhasil merespons payload yang kompleks.")
                print("Ini berarti masalah 'hanging' ada di dalam lingkungan server FastAPI Anda, bukan pada koneksi/payload.")
                try:
                    response_data = response.json()
                    print("\n--- Data Respons ---")
                    print(json.dumps(response_data, indent=2))
                    print("--------------------")
                except json.JSONDecodeError:
                    print(f"Respons mentah: {response.text}")
            else:
                print(f"\n\033[91mHASIL: GAGAL - ERROR HTTP {response.status_code}\033[0m")
                print("Meskipun gagal, ini tetap hasil yang baik karena server tidak menggantung.")
                print(f"Respons error mentah: {response.text}")

    except httpx.TimeoutException:
        print(f"\n\033[91mHASIL: GAGAL - TIMEOUT\033[0m")
        print("Permintaan ke OpenRouter timeout. Ini mengindikasikan masalah jaringan atau OpenRouter sedang lambat.")
        print("Masalah ini kemungkinan besar adalah akar dari masalah 'hanging' di server Anda.")
    except httpx.RequestError as e:
        print(f"\n\033[91mHASIL: GAGAL - ERROR JARINGAN\033[0m")
        print(f"Tidak dapat terhubung ke OpenRouter: {e}")
    except Exception as e:
        print(f"\n\033[91mHASIL: GAGAL - ERROR SKRIP\033[0m")
        print(f"Terjadi error yang tidak terduga: {e}")

if __name__ == "__main__":
    asyncio.run(test_full_payload())
