# WebFlask

Starter template aplikasi web berbasis **Flask 3** dengan pemisahan struktur **Backend** (`backend/`) dan **Frontend** (`frontend/`) dalam satu server Flask, lengkap dengan SQLite authentication API, konfigurasi environment, custom error handler (HTML & JSON), automated smoke/auth test, dan baseline security headers.

## Fitur Utama

- **Arsitektur Layered MVC (Controller -> Service -> Repository + Frontend Views)**:
  - **Controllers (`backend/controllers/`)**: Auto-discovered `*_controller.py` yang mengekspor `bp = Blueprint(...)`, berisi handler HTTP tipis tanpa `try/except` berulang.
  - **Services (`backend/services/`)**: Menampung business logic, validasi domain, hashing `scrypt`, dan raise `AppError` (`backend/exceptions.py`).
  - **Repositories (`backend/repositories/`)**: Khusus query SQLite dengan helper bersama di `base.py`.
  - **Views (`frontend/`)**: Template Jinja2 (`frontend/templates/`) dan aset statis (`frontend/static/`).
- **Application Factory**: Terpusat di `backend/__init__.py` dengan registrasi blueprint, error handler, dan security middleware.
- **SQLite Auth & Session Hardening**: Penyimpanan user (`scrypt` password hashing via Werkzeug) dan server-side session table di `instance/app.db`, cookie `__Host-session` (`HttpOnly`, `Secure`, `SameSite=Lax`, expiry 30 menit), proteksi CSRF (`X-CSRF-Token`), serta in-memory rate limiting.
- **Konfigurasi Environment**: Kelas `DevelopmentConfig`, `TestingConfig`, dan `ProductionConfig` di `config.py`.
- **Custom Error Pages & JSON Errors**: Handler `404`, `405`, dan `500` di `backend/controllers/error_controller.py` mengembalikan HTML untuk halaman web dan JSON untuk `/api/*` tanpa membocorkan stack trace.
- **Security Headers Default**: `Content-Security-Policy` (`'self'`), `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`, `Referrer-Policy`, dan `Permissions-Policy`.
- **Automated Tests**: Smoke test dan auth security test di `tests/test_app.py` dan `tests/test_auth.py` menggunakan `unittest` bawaan Python.

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
│   ├── db.py
│   ├── exceptions.py
│   ├── http.py
│   ├── schema.sql
│   ├── security.py
│   ├── controllers/
│   │   ├── __init__.py
│   │   ├── api_controller.py
│   │   ├── auth_controller.py
│   │   ├── error_controller.py
│   │   └── web_controller.py
│   ├── repositories/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── session_repository.py
│   │   └── user_repository.py
│   └── services/
│       ├── __init__.py
│       └── auth_service.py
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
    ├── test_app.py
    └── test_auth.py
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

Tabel SQLite di `instance/app.db` otomatis dibuat saat aplikasi pertama kali dijalankan (bisa juga diinisialisasi manual lewat `flask --app app init-db`).

Endpoint yang tersedia di `http://127.0.0.1:5000`:

- Web homepage: `GET /`
- API health check: `GET /api/health`
- Ambil CSRF token: `GET /api/auth/csrf`
- Register user: `POST /api/auth/register` (header `X-CSRF-Token`, JSON `{"email", "password"}`)
- Login: `POST /api/auth/login` (header `X-CSRF-Token`, JSON `{"email", "password"}`)
- Profile aktif: `GET /api/auth/me`
- Logout: `POST /api/auth/logout` (header `X-CSRF-Token`)

## Menjalankan Test

```powershell
.\venv\Scripts\python.exe -m unittest discover -s tests -v
```

## Catatan Keamanan & Production

- Development server (`app.run()`) dikonfigurasi hanya untuk `127.0.0.1` dan tidak boleh dipakai di production.
- Di mode `production`, environment variable `SECRET_KEY` **wajib** diset (aplikasi akan error jika kosong).
- Cookie sesi memakai prefix `__Host-` dan flag `Secure`; di production wajib berjalan di belakang HTTPS/TLS.
- Rate limiter bawaan memakai memori proses tunggal; untuk deployment multi-worker gunakan backend bersama (misalnya Redis dengan `Flask-Limiter`).
- Untuk deployment production, jalankan objek `app` dari `app.py` menggunakan WSGI server seperti **Waitress** (Windows) atau **Gunicorn** (Linux).
