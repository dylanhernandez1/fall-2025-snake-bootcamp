# CSAI Fall 2025 Snake Bootcamp

This repository features a machine learning-powered Snake game, seamlessly integrated with a Next.js frontend using Socket.IO for real-time communication.

## Prerequisites

Before you begin, ensure you have the following installed:

- **Node.js** (v18 or higher): [Download Node.js](https://nodejs.org/)
- **npm** (comes with Node.js)
- **Python** (version 3.9): [Download Python](https://www.python.org/downloads/release/python-390/)

You can verify installations with:

```bash
node -v
npm -v
python3 --version
```

## Getting Started

Follow these steps to run the project locally on **macOS**, **Windows**, or **Linux**.

### Frontend

```bash
cd apps/frontend
npm install
npm run dev
```

### Backend

#### Create and activate a Python virtual environment

- **macOS/Linux:**

  ```bash
  cd apps/backend
  python3 -m venv .venv
  source .venv/bin/activate
  ```

- **Windows (Command Prompt):**

  ```cmd
  cd apps\backend
  python -m venv .venv
  .venv\Scripts\activate
  ```

- **Windows (PowerShell):**

  ```powershell
  cd apps\backend
  python -m venv .venv
  .venv\Scripts\Activate.ps1
  ```

#### Install dependencies and start the backend

```bash
pip install -r requirements.txt
python src/app.py
```

Once both servers are running, open [http://localhost:3000](http://localhost:3000) in your browser.
