# WebFlask

Starter template aplikasi web sederhana berbasis **Flask 3** dengan struktur modular, template Jinja2, konfigurasi berbasis environment, custom error handler, automated smoke test, dan baseline security headers.

## Fitur Utama

- **Application Factory & Blueprint**: Terpisah di `app/__init__.py` dan `app/routes.py` agar mudah diskalakan.
- **Konfigurasi Environment**: Kelas `DevelopmentConfig`, `TestingConfig`, dan `ProductionConfig` di `config.py`.
- **Template Inheritance**: Layout terpusat di `app/templates/base.html` dengan auto-escaping bawaan Jinja2.
- **Custom Error Pages**: Handler `404` dan `500` di `app/errors.py` dengan template khusus tanpa membocorkan stack trace.
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
├── app/
│   ├── __init__.py
│   ├── errors.py
│   ├── routes.py
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

Aplikasi berjalan di `http://127.0.0.1:5000`.

## Menjalankan Test

```powershell
.\venv\Scripts\python.exe -m unittest discover -s tests -v
```

## Catatan Keamanan & Production

- Development server (`app.run()`) dikonfigurasi hanya untuk `127.0.0.1` dan tidak boleh dipakai di production.
- Untuk deployment production, jalankan objek `app` dari `app.py` menggunakan WSGI server seperti **Waitress** (Windows) atau **Gunicorn** (Linux), serta set `FLASK_ENV=production`.
- Jika nanti menambahkan form, sesi pengguna, atau autentikasi, pastikan menambahkan `SECRET_KEY` via environment variable/secret manager, proteksi CSRF, dan rate limiting.
