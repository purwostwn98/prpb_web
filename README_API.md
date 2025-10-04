# Truck Management API

API ini menggunakan Django REST Framework dan JWT (SimpleJWT) untuk autentikasi. Semua endpoint CRUD (Create, Read, Update, Delete) dan endpoint login/logout/refresh JWT tersedia.

## Autentikasi
- Semua endpoint (kecuali login/refresh/logout) membutuhkan JWT access token.
- Sertakan header berikut pada setiap request:
  ```
  Authorization: Bearer <access_token>
  ```

## Endpoint Autentikasi

### 1. Login
- **POST** `/api/login/`
- Body:
  ```json
  {
    "username": "<username>",
    "password": "<password>"
  }
  ```
- Response:
  ```json
  {
    "refresh": "<refresh_token>",
    "access": "<access_token>"
  }
  ```

### 2. Refresh Token
- **POST** `/api/refresh/`
- Body:
  ```json
  {
    "refresh": "<refresh_token>"
  }
  ```
- Response:
  ```json
  {
    "access": "<new_access_token>"
  }
  ```

### 3. Logout (Blacklist Refresh Token)
- **POST** `/api/logout/`
- Body:
  ```json
  {
    "refresh": "<refresh_token>"
  }
  ```
- Header: Authorization: Bearer <access_token>

## Catatan
- Semua endpoint CRUD di atas wajib menyertakan header Authorization.
- Gunakan Postman/curl untuk mencoba endpoint.
- Token JWT didapat dari endpoint login.

---

## Import Postman Collection
Untuk memudahkan testing, tersedia file Postman collection di folder `api/postman_collection/`.

Cara import:
1. Buka Postman
2. Pilih `Import` > `Upload Files`
3. Pilih file `Truck Management.postman_collection.json` dari folder `api/postman_collection/`
4. Semua endpoint siap dicoba di Postman

