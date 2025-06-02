# 🧠 TCGBrain – AI-Powered Knowledge Management System

TCGBrain is an intelligent organizational assistant developed by TCG. It leverages AI to streamline knowledge sharing, answer department-specific questions, generate reports, support dashboards, and assist with digital documentation across teams.

## 🚀 Features

- 💬 Conversational AI (TCG Assistant) for internal team queries
- 📄 Document ingestion & retrieval (PDF, Word, PowerPoint)
- 🧠 AI-powered Q&A and content generation
- 🔐 Access control and department-specific customization


## 🛠️ Tech Stack

- **Backend**: Python (Flask)
- **AI/LLM**: Google Gemini
- **Frontend**: React 
- **Database**: PostgreSQL
- **Document Handling**: PyMuPDF, python-docx, python-pptx
- **Authentication**: JWT / OAuth2 (Coming soon)

## 📁 Folder Structure

```

tcgbrain/
│
├── backend/
│   ├── api/
│   ├── services/
│   ├── utils/
│   ├── models/
│   └── main.py
│
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   └── App.jsx
│
└── README.md

````

## 📦 Setup Instructions

### 🧑‍💻 Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # on Windows use `venv\Scripts\activate`
pip install -r requirements.txt
gunicorn main:app
````

## 📌 Usage

1. Upload your internal documents.
2. Ask TCG Assistant department-specific questions.
3. Generate reports and summaries from large documents.
4. Collaborate better with instant knowledge retrieval.

## 🧪 TODO

* [ ] Report & dashboard generation support
* [ ] Cloud storage + scalable architecture
* [ ] Improve multi-language support
* [ ] Role-based access control
* [ ] Audit logging & feedback loop for answers

## 🤝 Contributing

Contributions are welcome! To propose a change:

1. Fork the repo
2. Create a new branch
3. Make your changes
4. Submit a pull request
