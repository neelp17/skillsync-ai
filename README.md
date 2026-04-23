# SkillSync AI

SkillSync AI is an AI-powered skill gap analyzer that helps users upload a resume, extract technical skills, and generate a roadmap for a target role.

The project currently uses a static frontend built with HTML, CSS, and JavaScript, and a Python FastAPI backend connected to the Gemini API.

## Features

- Upload a resume PDF
- Extract technical skills from the resume
- Enter a target role
- Generate an AI-based roadmap for the selected role
- Fallback skill extraction and analysis when Gemini is unavailable
- Simple, clean frontend flow for upload and result viewing

## Tech Stack

### Frontend

- HTML
- CSS
- JavaScript

### Backend

- Python
- FastAPI
- httpx
- pdfplumber
- python-dotenv

### AI

- Gemini API

## Project Structure

```text
SkillSync AI/
├── backend/
│   ├── .env.example
│   ├── check_models.py
│   ├── config.py
│   ├── main.py
│   ├── requirements.txt
│   ├── routes/
│   │   ├── __init__.py
│   │   └── analyzer.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── ai_service.py
│   │   └── resume_parser.py
│   └── utils/
│       └── __init__.py
├── frontend/
│   ├── assets/
│   ├── css/
│   │   └── style.css
│   ├── js/
│   │   └── app.js
│   ├── dashboard.html
│   └── index.html
└── README.md
```

## How It Works

1. The user uploads a resume from the frontend.
2. The FastAPI backend extracts text from the PDF.
3. The backend sends the content to Gemini for skill extraction.
4. The user enters a target role.
5. The backend generates a roadmap and returns it to the frontend.
6. The frontend displays the result on the dashboard page.

## Local Setup

### 1. Clone the repository

```bash
git clone https://github.com/neelp17/skillsync-ai.git
cd skillsync-ai
```

### 2. Set up the backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Create environment file

Create a file named `.env` inside the `backend/` folder and add:

```env
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-2.5-flash-lite
```

### 4. Run the FastAPI backend

```bash
uvicorn main:app --reload
```

Backend runs at:

```text
http://127.0.0.1:8000
```

### 5. Run the frontend

Open `frontend/index.html` in your browser.

Note: the frontend currently calls the backend at:

```text
http://127.0.0.1:8000
```

## API Endpoints

### `GET /`

Health check endpoint.

### `POST /upload`

Uploads a resume PDF and extracts skills.

### `POST /analyze`

Accepts user skills and a target role, then returns an AI-generated roadmap.

## Current Limitations

- No database yet
- No user login system yet
- Results are stored in browser local storage on the frontend
- Frontend is currently configured for local backend URL

## Planned Enhancements

- Save analysis history using a database
- Add email or user-based roadmap management
- Add single active roadmap workflow
- Dockerize the backend
- Deploy frontend and backend on AWS
- Add Terraform for infrastructure provisioning
- Add CI/CD with GitHub Actions

## Cloud and DevOps Direction

This project is being prepared as a cloud/devops-focused portfolio project. The planned deployment path is:

- Frontend on AWS S3 + CloudFront
- Backend on AWS App Runner or ECS Fargate
- Secrets managed through environment variables or AWS Secrets Manager
- Infrastructure managed using Terraform
- CI/CD using GitHub Actions

## Author

Neel V Padmawar
