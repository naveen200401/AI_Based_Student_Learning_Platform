# 🧠 AI Student Learning Platform

AI Student Learning Platform is an AI-powered quiz and question answering web application built with Python. It combines user authentication, quiz generation, and retrieval-augmented generation (RAG) to deliver intelligent responses and interactive quizzes using AI.

Built with:
- Python (Flask) for backend
- HTML & Jinja templates for frontend
- RAG-style AI integration for enhanced question answering
- Modular structure with authentication and database support

## 🚀 Features

- ✨ **User Authentication** — Register, login, and manage sessions (in `auth/`)
- 📝 **Dynamic Quiz System** — Create, view, and take quizzes (in `quiz/`)
- 🔎 **RAG-based AI Answers** — Intelligent question answering using retrieval-augmented techniques (in `rag/`)
- 📁 **Models and DB** — SQLAlchemy models and database setup
- 📄 **Config & Setup** — Central configuration in `config.py`

## 📁 Repository Structure

```
AI_Based_Student_Learning_Platform/
├── auth/                # Authentication routes & views
├── quiz/                # Quiz creation & gameplay
├── rag/                 # RAG/AI logic and utilities
├── templates/           # HTML templates
├── uploads/             # Uploaded assets
├── config.py            # App configuration
├── app.py               # Flask application entrypoint
├── models.py            # Database models
├── create_db.py         # Script to initialize database
└── .gitignore
```

## 🛠️ Getting Started

### ✨ Prerequisites

Make sure you have:
- Python 3.10+
- Virtual environment (venv)
- Git

### 📦 Installation

1. **Clone the repository**

```bash
git clone https://github.com/naveen200401/AI_Based_Student_Learning_Platform.git
cd AI_Based_Student_Learning_Platform
```

2. **Create & activate a virtual environment**

```bash
python3 -m venv venv
source venv/bin/activate      # macOS/Linux
venv\Scripts\activate         # Windows
```

3. **Install dependencies**

```bash
pip install -r requirements.txt
```

### ⚙️ Configuration

Update configuration in `config.py`:

| Setting | Purpose |
|---------|---------|
| SECRET_KEY | Flask session & security |
| DATABASE_URI | Path to your SQL database |
| AI_API_KEY | Key for AI / RAG service |

Replace `AI_API_KEY` with your AI provider API key (OpenAI, etc).

### 🧠 Running the App

1. **Initialize database**

```bash
python create_db.py
```

2. **Start server**

```bash
python app.py
```

3. **Open in browser**

```
http://localhost:5000
```

## 📝 Usage

| Feature | Route |
|---------|-------|
| Register | `/auth/register` |
| Login | `/auth/login` |
| Quiz List | `/quiz` |
| AI Question Answering | (endpoint in `rag/` -- call via frontend form) |

### 🧪 Example UI

The app includes forms for:
- Register / Login
- Quiz creation
- Question submission to AI

## 🛡️ Security & Deployment

To deploy:
- Use a WSGI server (Gunicorn / uWSGI)
- Enable HTTPS
- Store sensitive keys in environment variables

## 🧩 Contributing

PRs are welcome!

1. Fork the repo
2. Create feature branch
3. Submit a Pull Request

## 📜 License

This project currently has no license file. Add a LICENSE if needed.

## 🙌 Acknowledgements

Built by Naveen as an educational project combining Flask, AI, and RAG technologies.
