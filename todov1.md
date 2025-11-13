Prioritas Tinggi: Mengisi Kesenjangan Fitur Utama

  Tugas-tugas ini menangani fitur yang terlihat di antarmuka pengguna (UI) tetapi belum memiliki implementasi backend yang
  fungsional.

   1. Implementasikan "Quick Actions" di Dasbor:
       * Tugas: Ganti endpoint placeholder untuk "Quick Actions" dengan logika bisnis yang sebenarnya.
       * File Terkait: server_python/main.py
       * Endpoint:
           * POST /api/neosyntis/open-lab
           * POST /api/arcana/start-chat
           * POST /api/myntrix/deploy-model
           * POST /api/myntrix/manage-agents

   2. Selesaikan Fitur Pengiriman Pekerjaan (Job) Myntrix:
       * Tugas: Buat dan uji endpoint untuk membuat pekerjaan baru di Myntrix, untuk mendukung JobSubmissionForm.tsx.
       * File Terkait: server_python/myntrix/api.py, server_python/myntrix/crud.py
       * Endpoint yang Diperlukan: POST /api/myntrix/jobs/

   3. Implementasikan Integrasi GitHub untuk Profil Pengguna:
       * Tugas: Tambahkan logika backend untuk menangani autentikasi OAuth GitHub, serta menyimpan dan mengelola token akses
         pengguna.
       * File Terkait: server_python/auth.py, server_python/database.py, server_python/main.py
       * Langkah:
           * Tambahkan kolom untuk token GitHub di tabel User pada database.py.
           * Buat endpoint API baru untuk memulai alur OAuth dan menangani callback dari GitHub.

   4. Kembangkan Fitur "Ecosystem Builder" Neosyntis:
       * Tugas: Rancang dan implementasikan model database dan API yang diperlukan untuk fitur "Ecosystem Builder".
       * File Terkait: server_python/neosyntis/api.py, server_python/neosyntis/crud.py, server_python/database.py
       * Langkah:
           * Definisikan skema database baru yang relevan.
           * Buat endpoint CRUD untuk mengelola entitas "Ecosystem".

  Prioritas Menengah: Menyempurnakan Fitur yang Ada

  Tugas-tugas ini berfokus pada penggantian data mock dengan logika nyata dan menyempurnakan fungsionalitas yang sudah ada
  sebagian.

   5. Tingkatkan Status Sistem Dasbor dengan Data Real-time:
       * Tugas: Ganti semua nilai yang di-hardcode/disimulasikan (misalnya, jobsCompleted, requestsRouted) di endpoint
         /api/system/status dengan agregasi data nyata dari database.
       * File Terkait: server_python/main.py

   6. Implementasikan Logika Eksekusi Nyata untuk Myntrix & Neosyntis:
       * Tugas: Ganti logika simulasi dengan interaksi sistem yang sebenarnya.
       * File Terkait: server_python/myntrix/api.py, server_python/neosyntis/api.py
       * Endpoint:
           * Myntrix: POST /agents/{agent_id}/start, stop, restart (kontrol proses/kontainer), POST /tasks/{task_id}/run (eksekusi
              skrip/fungsi).
           * Neosyntis: POST /workflows/{workflow_id}/trigger (mesin alur kerja), POST /models/{model_id}/deploy (integrasi dengan
              platform serving model), POST /models/{model_id}/train (integrasi dengan framework ML).

   7. Implementasikan Interaksi Perangkat Keras (Hardware) Nyata di Myntrix:
       * Tugas: Kembangkan driver atau protokol komunikasi (Serial, MQTT, dll.) untuk endpoint yang berinteraksi dengan perangkat.
       * File Terkait: server_python/myntrix/api.py
       * Endpoint: POST /devices/{device_id}/connect, disconnect, command, upload.

  Prioritas Rendah: Peningkatan & Ketahanan Sistem

  Tugas-tugas ini meningkatkan kualitas dan ketahanan kode.

   8. Terapkan Logika Fallback untuk Metrik Sistem:
       * Tugas: Selesaikan implementasi strategi fallback di GET /system-metrics yang menggunakan data mock jika psutil gagal
         karena masalah izin (seperti di Termux).
       * File Terkait: server_python/myntrix/api.py
       * Status: Contoh kode sudah ada di ImplementationV5.md dan siap untuk diterapkan.

   9. Perluas Fungsionalitas Pencarian Neosyntis:
       * Tugas: Tambahkan logika untuk mencari entitas ML Model di endpoint GET /api/neosyntis/search.
       * File Terkait: server_python/neosyntis/api.py
