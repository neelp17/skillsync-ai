# SkillSync AI

SkillSync AI is a resume skill analyzer and personalized roadmap generator. The repository contains a static HTML/CSS/JavaScript frontend, a FastAPI backend, Gemini-powered analysis with a fallback, and PostgreSQL persistence for saved analyses.

## Features

- Upload a PDF resume and extract skills.
- Generate a skill gap analysis and roadmap for a target role.
- Save analyses in PostgreSQL and list, view, update, or delete history.
- Run locally with Docker Compose or run the API directly with SQLite for development.
- Provision a single EC2 host with Terraform and deploy on pushes to `main` with GitHub Actions.

## Run locally with Docker

1. Install Docker Desktop / Docker Engine with the Compose plugin.
2. Copy `.env.example` to `.env`, set a strong `POSTGRES_PASSWORD`, and set a newly rotated `GEMINI_API_KEY`.
3. Run `docker compose up --build`.
4. Open `http://localhost`.

The API is available through the frontend proxy at `/api`; the backend itself is not exposed to the public host port. PostgreSQL data is stored in the `postgres_data` Docker volume.

## Run the backend without Docker

```powershell
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
uvicorn main:app --reload
```

The API defaults to a local SQLite file at `backend/skillsync.db`. Set `GEMINI_API_KEY` in `backend/.env` to enable Gemini; fallback analysis still works without it. Serve the `frontend/` directory with a local static server and change `frontend/config.js` to `http://127.0.0.1:8000` for direct API calls.

## API

- `GET /` health response
- `POST /upload` multipart PDF upload
- `POST /analyze` legacy non-persistent analysis endpoint
- `POST /analyses` generate and persist an analysis (JSON: `role`, `skills`)
- `GET /analyses` list the caller's saved history
- `GET /analyses/{id}` read one saved analysis
- `PATCH /analyses/{id}` update role and/or skills and regenerate the roadmap
- `DELETE /analyses/{id}` delete an analysis

The browser sends a stable UUID in `X-User-Id` to associate saved records with that browser profile. This is a portfolio/demo identity mechanism, **not authentication**: anyone able to set the header can impersonate an owner. Add real user authentication before using this with sensitive or public user data.

## AWS EC2 deployment

Terraform provisions an Ubuntu EC2 instance, an encrypted root volume, and a security group allowing HTTP plus SSH from the CIDR you specify. PostgreSQL runs as a Compose service on that host with a persistent Docker volume.

1. Create/select an AWS account, a default VPC, and an EC2 key pair.
2. From `terraform/`, copy `terraform.tfvars.example` to `terraform.tfvars`; set your SSH public IP as `/32` and your key pair name.
3. Run `terraform init`, review `terraform plan`, then `terraform apply`. Save the `public_ip` output.
4. In GitHub repository settings, add variable `EC2_HOST` with that IP and secrets `EC2_SSH_PRIVATE_KEY`, `POSTGRES_PASSWORD`, and the **rotated** `GEMINI_API_KEY`.
5. Push to `main`. The workflow runs Python checks and container builds, then copies the project to EC2 and runs `docker compose up -d --build`.

The deploy job is skipped if `EC2_HOST` is unset. Terraform state is local by default; keep it private and back it up securely. This setup serves HTTP only; add a domain and HTTPS termination before using it for real users. The AWS resources incur charges while running; `terraform destroy` removes the instance and its attached database volume.

## CI

GitHub Actions runs on pull requests and pushes to `main`: Python bytecode compilation, API CRUD tests, and frontend/backend image builds. Deployment runs after verification only for `main` pushes when the `EC2_HOST` repository variable is configured.

## Secrets and archive hygiene

Never commit `.env`, Terraform state, private keys, or API credentials. The supplied project ZIP contains `backend/.env`; treat its Gemini key as exposed and revoke/rotate it before pushing or deploying. Create a clean source archive without `.git`, virtual environments, or `.env` files.
