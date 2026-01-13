# Subscribo - Secure Subscription Management

Subscribo is a subscription-based mobile application built with **Flutter** (Frontend) and **FastAPI** (Backend). It demonstrates secure purchase verification, user entitlement management, and real-time subscription lifecycle handling.

## 🚀 Quick Start (Dev Mode)

**Note**: You can run this application in "Dev Mode" without Google Play or Firebase credentials. The backend will use mock verification logic.

### 1. Backend Setup (Python)

Prerequisites: Python 3.9+, PostgreSQL.

1.  Navigate to `backend/`.
2.  Create a virtual environment:
    ```bash
    python -m venv venv
    .\venv\Scripts\activate
    ```
3.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
4.  Configure `.env` (See [Environment Variables](#environment-variables) below).
5.  Run the server:
    ```bash
    uvicorn main:app --reload
    ```
    Server runs at `http://127.0.0.1:8000`.

### 2. Mobile Setup (Flutter)

1.  Navigate to `mobile/`.
2.  Install dependencies:
    ```bash
    flutter pub get
    ```
3.  Run on emulator:
    ```bash
    flutter run
    ```

---

## 🔑 Environment Variables

Create a file named `.env` in the `backend/` directory.

### Required
These variables are necessary for the app to start and connect to the database.

| Variable | Description | Example |
| :--- | :--- | :--- |
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://user:pass@localhost:5432/subscribe` |

### Optional (For Real Production Verification)
If these are missing, the app defaults to **MOCK MODE** (always verifies purchases as valid).

| Variable | Description |
| :--- | :--- |
| `GOOGLE_APPLICATION_CREDENTIALS` | Path to Google Service Account JSON. Used for Google Play Developer API. |
| `PACKAGE_NAME` | Android Package Name (e.g., `com.example.subscribo`). |
| `FIREBASE_CREDENTIALS` | (Optional) Path to Firebase Admin JSON if not using default credentials. |

---

## 📂 Project Structure

-   **`mobile/`**: Flutter application.
    -   `services/iap_service.dart`: Handles Google Play Billing interactions.
    -   `services/api_service.dart`: Communicates with backend.
-   **`backend/`**: FastAPI application.
    -   `routers/purchase.py`: Verifies tokens. **Contains Mock Logic fallback.**
    -   `routers/rtdn.py`: Handles Real-Time Developer Notifications (Pub/Sub).
    -   `models.py`: Database schema (Users, Subscriptions).

## 🛠 Features

-   **Purchase Verification**: Validates purchase tokens against Google Play (or Mock).
-   **User Sync**: Syncs Firebase/Anonymous users to Postgres.
-   **Entitlements**: Dynamic access control based on valid subscription.
-   **Resilient**: Falls back gracefully if external APIs are not configured.
