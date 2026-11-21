# WebFlask

Starter template aplikasi web berbasis **Flask 3** dengan pemisahan struktur **Backend** (`backend/`) dan **Frontend** (`frontend/`) dalam satu server Flask, lengkap dengan konfigurasi environment, custom error handler (HTML & JSON), automated smoke test, dan baseline security headers.

## Fitur Utama

- **Pemisahan Backend & Frontend**: Kode Python, Blueprint web/API, dan error handler berada di `backend/`; template Jinja2 dan aset statis berada di `frontend/`.
- **Application Factory & Blueprint**: Terpusat di `backend/__init__.py` dengan rute terpisah di `backend/routes/web.py` (UI) dan `backend/routes/api.py` (JSON `/api/*`).
- **Konfigurasi Environment**: Kelas `DevelopmentConfig`, `TestingConfig`, dan `ProductionConfig` di `config.py`.
- **Template Inheritance**: Layout terpusat di `frontend/templates/base.html` dengan auto-escaping bawaan Jinja2.
- **Custom Error Pages & JSON Errors**: Handler `404`, `405`, dan `500` di `backend/errors.py` mengembalikan HTML untuk halaman web dan JSON untuk `/api/*` tanpa membocorkan stack trace.
- **Security Headers Default**: `Content-Security-Policy` (`'self'`), `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`, `Referrer-Policy`, dan `Permissions-Policy`.
- **Automated Tests**: Smoke test dan verifikasi header keamanan di `tests/test_app.py` menggunakan `unittest` bawaan Python.

## Struktur Proyek

```text
WebFlask/
├── .env.example
├── .gitignore
├── README.md
├── app.py
├── config.py
├── requirements.txt
├── backend/
│   ├── __init__.py
│   ├── errors.py
│   └── routes/
│       ├── __init__.py
│       ├── api.py
│       └── web.py
├── frontend/
│   ├── static/
│   │   └── css/
│   │       └── style.css
│   └── templates/
│       ├── base.html
│       ├── index.html
│       └── errors/
│           ├── 404.html
│           └── 500.html
└── tests/
    └── test_app.py
```

## Prasyarat

- Python 3.10+
- `pip` dan `venv`

## Instalasi

```powershell
# 1. Buat virtual environment
python -m venv venv

# 2. Install dependensi
.\venv\Scripts\python.exe -m pip install -r requirements.txt
```

*(Untuk Linux/macOS, gunakan `./venv/bin/python` sebagai pengganti `.\venv\Scripts\python.exe`.)*

## Menjalankan Aplikasi (Local Development)

Salin `.env.example` jika ingin mengatur variabel environment secara lokal, atau set langsung di shell:

```powershell
$env:FLASK_ENV="development"
.\venv\Scripts\python.exe app.py
```

Aplikasi berjalan di `http://127.0.0.1:5000`:

- Web homepage: `GET http://127.0.0.1:5000/`
- API health check: `GET http://127.0.0.1:5000/api/health`

## Menjalankan Test

```powershell
.\venv\Scripts\python.exe -m unittest discover -s tests -v
```

## Catatan Keamanan & Production

- Development server (`app.run()`) dikonfigurasi hanya untuk `127.0.0.1` dan tidak boleh dipakai di production.
- Untuk deployment production, jalankan objek `app` dari `app.py` menggunakan WSGI server seperti **Waitress** (Windows) atau **Gunicorn** (Linux), serta set `FLASK_ENV=production`.
- Jika nanti menambahkan form, sesi pengguna, atau autentikasi/endpoint API privat, pastikan menambahkan `SECRET_KEY` via environment variable/secret manager, proteksi CSRF, autentikasi, validasi input, dan rate limiting.
