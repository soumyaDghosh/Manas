# Manas

A FastAPI backend for a chat application with AI-powered mood analysis and session journaling. This service handles real-time chat processing, mood analysis via Gemini AI, and session storage in Firestore, with Redis as temporary storage. Firebase Auth is used for user authentication.

This backend is designed to work seamlessly with a **Flutter-based frontend**, which provides the chat UI and interacts with the backend APIs.



## Table of Contents

* [Features](#features)
* [Architecture](#architecture)
* [Endpoints](#endpoints)
* [Data Flow](#data-flow)
* [Installation](#installation)
* [Configuration](#configuration)
* [Running the App](#running-the-app)
* [Flutter Frontend](#flutter-frontend)
* [Dependencies](#dependencies)
* [Contributing](#contributing)
* [License](#license)



## Features

* **Flutter frontend** with real-time chat UI
* **FastAPI backend** for chat processing
* **AI mood analysis** per message and per session
* **Session journaling** stored in Firestore
* **Redis cache** for temporary message storage
* **Firebase Auth** for authentication



## Architecture

**Components:**

1. **Flutter Frontend**

   * Built with Flutter for cross-platform support (Android, iOS, Web).
   * Handles user login via Firebase Auth.
   * Sends chat messages to backend APIs.
   * Displays AI replies, moods, and past session journals.

2. **FastAPI Backend**

   * Middleware validates Firebase Auth tokens.
   * Provides `/api/v1/process`, `/api/v1/end-session`, and `/api/v1/sessions` endpoints.

3. **Redis Cache**

   * Temporarily stores active chat messages and mood analyses.

4. **Gemini AI**

   * Provides mood analysis and AI-generated replies.
   * Summarizes session at the end.

5. **Firestore**

   * Permanent storage for completed sessions (mood, summary, timestamp).



## Endpoints

### `/api/v1/process`

Handles a single chat message -> calls Gemini AI -> stores results in Redis -> returns AI reply.

### `/api/v1/end-session`

Ends session -> retrieves full chat history from Redis -> summarizes via Gemini -> stores results in Firestore.

### `/api/v1/sessions`

Fetches session journals from Firestore and returns them to the frontend.



## Data Flow

1. User logs in via Firebase Auth in **Flutter frontend**.
2. Frontend sends chat messages -> `/api/v1/process`.
3. Backend calls Gemini AI -> returns AI reply + mood -> stores in Redis.
4. On session end -> `/api/v1/end-session` -> Gemini AI summarizes -> backend stores result in Firestore.
5. Frontend calls `/api/v1/sessions` -> retrieves past journals (mood, summary, timestamp).



## Installation

```bash
git clone https://github.com/soumyaDghosh/manas.git
cd manas
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows
pip install -r requirements.txt
```



## Configuration

`.env` file:

```env
GEMINI_API_KEY=<api-key>
REDIS_HOST=<redis-hort>
REDIS_PORT=<redis-port>
REDIS_USERNAME=<redis-username>
REDIS_PASSWORD=<redis-password>
FIREBASE_CREDENTIALS=<firebase-config-json-flattened>
```



## Running the App

### Running the backend

```bash
uvicorn backend.app.main:app --reload
```

Visit `http://localhost:8000/docs` for API docs.

### Running the frontend

Make sure you've [flutterfire](https://firebase.google.com/docs/flutter/setup) configured.

```
cd frontend
flutter build apk
```

Voilah! You got your apk to run.



## Flutter Frontend

* The companion frontend is built using **Flutter**.
* Handles user authentication with **Firebase Auth**.
* Sends chat messages to the FastAPI backend and renders AI replies in real time.
* Displays mood indicators and session journals fetched from Firestore through the `/api/v1/sessions` endpoint.
* Provides a seamless cross-platform experience (Android, iOS, Web).



## Dependencies

* FastAPI
* Uvicorn
* Redis (`redis-py`)
* Firebase Admin SDK
* Firestore
* Gemini AI SDK/API
* Pydantic



## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Commit changes: `git commit -m "Add your feature"`
4. Push branch: `git push origin feature/your-feature`
5. Open a Pull Request



## License

This project is licensed under the AGPL-3.0 License.
