# Roadmap & Jurnal Implementasi Arsitektur V1

**Dokumen ini bertujuan untuk melacak proses, progres, dan keputusan desain dalam mengimplementasikan arsitektur orkestrasi agen V1 untuk Vareon.**

---

## 1. Visi & Tujuan

Tujuan utama adalah untuk merevolusi backend Vareon dari kumpulan modul terisolasi menjadi sebuah sistem multi-agen yang terorkestrasi secara cerdas. Kita akan membangun lapisan orkestrasi pusat di dalam **Cognisys** yang bertindak sebagai "otak strategis", yang dapat mendelegasikan tugas-tugas spesifik ke modul-modul lain (`Arcana`, `Neosyntis`, `Myntrix`) yang bertindak sebagai "agen pekerja spesialis".

---

## 2. Analisis Arsitektur Saat Ini (Ringkasan)

- **Cognisys:** Sistem saraf pusat. Mengelola model LLM, routing, dan deteksi niat. **Lokasi ideal untuk Orkestrator Utama.**
- **Arcana:** Eksekutor tugas. Kuat dalam menjalankan perintah, mengelola file, dan interaksi Git. **Akan menjadi 'Worker Agent' utama untuk tugas-tugas pengembangan.**
- **Myntrix:** Manajer aset. Mengelola siklus hidup "device" dan "agent" (proses). **Akan menyediakan 'Tools' untuk manajemen sumber daya.**
- **Neosyntis:** Manajer data & ML. Mengelola `datasets` dan `workflows`. **Akan menyediakan 'Tools' untuk operasi data dan MLOps.**

---

## 3. Roadmap Implementasi V1

### Fase 1: Fondasi & Protokol Komunikasi (A2A)

- [ ] **1.1: Definisikan Skema A2A di `cognisys/schemas.py`**
  - [ ] Buat Pydantic model `AgentTask` untuk standardisasi permintaan tugas antar-agen.
  - [ ] Buat Pydantic model `AgentResult` untuk standardisasi hasil tugas.
- [ ] **1.2: Modifikasi Skema Database**
  - [ ] Tambahkan kolom `parent_job_id` pada tabel `ArcanaAgentJob` untuk melacak hierarki tugas.

### Fase 2: Integrasi & Delegasi Tugas

- [ ] **2.1: Buat Tool Delegasi ke Arcana**
  - **Lokasi:** `server_python/cognisys/tools.py`
  - **Tindakan:** Implementasikan fungsi `delegate_task_to_arcana` yang memanggil endpoint `POST /api/arcana/agents/{agent_id}/execute` secara internal.
- [ ] **2.2: Tambahkan Tool untuk Modul Lain**
  - **Lokasi:** `server_python/cognisys/tools.py`
  - [ ] Implementasikan `trigger_neosyntis_workflow`.
  - [ ] Implementasikan `get_myntrix_device_status`.
  - [ ] Daftarkan semua tool baru ke dalam `tool_registry` Cognisys.

### Fase 3: Implementasi Orkestrator Inti

- [ ] **3.1: Refaktor Logika Inti Cognisys**
  - **Lokasi:** `server_python/cognisys/llm_interaction.py`
  - **Tindakan:** Ubah fungsi `process_chat_request` untuk bertindak sebagai `ManagerAgent`.
  - **Logika:** Ketika LLM mendeteksi niat yang memerlukan eksekusi (misal: `code_generation`), ia harus memanggil tool `delegate_task_to_arcana` alih-alih mencoba menanganinya sendiri.

### Fase 4: Pengujian & Validasi

- [ ] **4.1: Buat Tes Integrasi**
  - **Tindakan:** Buat skenario pengujian di mana sebuah prompt tingkat tinggi ke `Cognisys` berhasil didelegasikan dan dieksekusi oleh `Arcana`.

---

## 4. Jurnal Progres

- **18 November 2025:**
  - **Progres:** Dokumen roadmap ini dibuat. Rencana implementasi V1 yang disempurnakan telah disetujui.
  - **Langkah Berikutnya:** Memulai Fase 1 - Implementasi skema A2A di `cognisys/schemas.py`.

---

## 5. Keputusan Desain

- **Orkestrator di Cognisys:** Dipilih karena `Cognisys` sudah memiliki logika untuk deteksi niat dan routing, menjadikannya lokasi alami untuk pengambilan keputusan tingkat tinggi.
- **Arcana sebagai Worker:** Dipilih karena `Arcana` sudah memiliki implementasi *agentic loop* dan *tool-calling* yang matang untuk tugas-tugas eksekusi.
- **Komunikasi via API Internal:** Delegasi tugas akan dilakukan melalui panggilan API internal antar-modul, bukan pemanggilan fungsi langsung, untuk menjaga pemisahan dan skalabilitas.

---

## 6. Risiko & Pertimbangan

- **Perubahan Signifikan:** Refaktor di `cognisys/llm_interaction.py` akan menjadi perubahan yang signifikan dan memerlukan pengujian yang cermat untuk memastikan fungsionalitas yang ada tidak rusak.
- **Manajemen Konfigurasi:** Perlu ditentukan bagaimana `Cognisys` akan mengetahui `agent_id` dari `Arcana` yang akan digunakan untuk delegasi. Ini mungkin memerlukan konfigurasi baru.
