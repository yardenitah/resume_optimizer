# Resume Optimizer Backend

A **FastAPI**-based backend service for uploading, analyzing, and managing resumes, as well as saving and retrieving job postings. It integrates with **OpenAI**'s GPT models to analyze and score resumes against given job descriptions. Additionally, it supports searching for jobs on LinkedIn (via **Selenium**) and storing them in **MongoDB**.

---

## Table of Contents

- [Features](#features)  
- [Tech Stack](#tech-stack)  
- [Project Structure](#project-structure)  
- [Prerequisites](#prerequisites)  
- [Getting Started (Local Development)](#getting-started-local-development)  
  - [1. Clone Repository](#1-clone-repository)  
  - [2. Create and Fill Environment Variables](#2-create-and-fill-environment-variables)  
  - [3. Install Dependencies](#3-install-dependencies)  
  - [4. Run Locally](#4-run-locally)  
- [Running with Docker](#running-with-docker)  
  - [1. Build and Run Containers](#1-build-and-run-containers)  
  - [2. Access the Application](#2-access-the-application)  
- [API Endpoints](#api-endpoints)  
- [Environment Variables](#environment-variables)  
- [Contributing](#contributing)  
- [License](#license)  

---

## Features

1. **User Management**  
   - Secure user registration and login.  
   - Password hashing and JWT-based authentication (with optional admin privileges).

2. **Resume Management**  
   - Upload **PDF** or **DOCX** resumes to AWS S3.  
   - Retrieve, delete, and search resumes by title.  
   - Use OpenAI GPT-4 to analyze resumes and provide feedback or generate a match score.

3. **Job Management**  
   - Save job postings (manually or from LinkedIn).  
   - Link the best matching resume to each saved job posting.  
   - Search saved jobs by title and delete them if needed.

4. **LinkedIn Integration**  
   - **Selenium** is used to scrape/search for jobs on LinkedIn.  
   - Supports filtering by experience level and multiple job titles.

5. **CORS Configuration**  
   - Configured to allow requests from local React frontends at `http://localhost:3000`.

---

## Tech Stack

- **Python 3.10**  
- **FastAPI** (web framework)  
- **MongoDB** (database)  
- **Docker & Docker Compose** (containerization)  
- **OpenAI** (AI-powered resume analysis)  
- **AWS S3** (cloud storage for resumes)  
- **Selenium** (LinkedIn job search automation)  

---

## Project Structure

```text
resume_optimizer_backend/
│
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── database/
│   │   ├── __init__.py
│   │   ├── connection.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── resume.py
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── adminRoute.py
│   │   ├── resumeRoutes.py
│   │   ├── userRoutes.py
│   │   ├── jobRoutes.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── resumeService.py
│   │   ├── adminService.py
│   │   ├── userService.py
│   │   ├── jobService.py
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── admin_verification.py
│   │   ├── LinkedInManager.py
│   │   ├── s3_service.py
│   │   ├── file_extractor.py
│   │   ├── jwt.py
│   │   ├── gpt_utils.py
│   │   ├── validation.py
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .env
├── .gitignore
└── README.md
