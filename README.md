# AI-Powered Lead Prediction Engine 🚀

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![React](https://img.shields.io/badge/react-18-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.95%2B-teal)

This project is an **AI-driven solution designed to help sales teams prioritize leads** effectively. By combining traditional Machine Learning (Random Forest) with modern Generative AI (Gemini/Llama), it not only scores leads but also provides **detailed explainability** on *why* a lead is promising.

## 🌟 Key Features

*   **Smart Lead Scoring**: Automatically predicts conversion probability using a Random Forest classifier.
*   **AI Explainability**: Uses LLMs (Gemini/Llama) to generate human-readable reasons for each lead's score (e.g., "High engagement with pricing page").
*   **Interactive Chat**: "Chat with your Data" feature allowing sales reps to ask questions about leads in natural language.
*   **Real-time Dashboard**: Visual analytics and lead management interface built with React.
*   **Dual-Model Support**: Seamless failover between Google's **Gemini** (Cloud) and **Llama 3** (Local/Ollama) for robust performance.

## 🛠️ Tech Stack

### Backend
*   **Framework**: FastAPI (Python)
*   **ML Engine**: Scikit-Learn (Random Forest), Pandas, NumPy
*   **AI/LLM**: LangChain, Google Gemini API, Llama 3 (via Ollama/Llama.cpp)
*   **Caching**: Redis (for high-speed session & response caching)

### Frontend
*   **Framework**: React (Vite)
*   **Styling**: Tailwind CSS
*   **State Management**: React Hooks & Context API

### Infrastructure
*   **Containerization**: Docker & Docker Compose
*   **Database**: SQLite (for simplicity/demo), with support for Postgres/MySQL.

---

## 🚀 Getting Started

### Prerequisites
*   Python 3.10+
*   Node.js 16+
*   Redis (locally installed or via Docker)
*   Git

### 1. Clone the Repository
```bash
git clone https://github.com/Ruthless3217/AI-Lead-Prediction-Model.git
cd AI-Lead-Prediction-Model
```

### 2. Backend Setup
Navigate to the backend directory and set up the Python environment.

```bash
cd backend
python -m venv .venv
# Windows
.venv\Scripts\activate
# Mac/Linux
source .venv/bin/activate

pip install -r requirements.txt
```

**Configuration**: Create a `.env` file in the `backend/` directory with your API keys:
```env
GEMINI_API_KEY=your_gemini_key_here
REDIS_URL=redis://localhost:6379
```

### 3. Frontend Setup
Navigate to the frontend directory and install dependencies.

```bash
cd ../frontend
npm install
```

---

## 🏃‍♂️ Running the Application

### Option A: detailed (Manual)

**Start Backend Server:**
```bash
# In backend/ terminal
uvicorn main:app --reload --port 8000
```

**Start Frontend Client:**
```bash
# In frontend/ terminal
npm run dev
```

Access the app at `http://localhost:5173`.

### Option B: Docker (Recommended)
You can spin up the entire stack (Frontend + Backend + Redis) with one command:

```bash
docker-compose up --build
```

---

## 📚 Documentation
For a deep dive into the architecture and code structure, check out the [Project Walkthrough](./Project_Walkthrough.md).

## 🤝 Contributing
Contributions are welcome! Please fork the repository and submit a Pull Request.

## 📄 License
This project is licensed under the MIT License.
