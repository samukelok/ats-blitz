# ⚡ ATSBlitz — AI-Powered Resume Analyzer

[🌐 Live Demo  →  atsblitz.bluenroll.co.za](https://atsblitz.bluenroll.co.za)

ATSBlitz is an AI-powered resume/CV analyzer designed to help job seekers tailor their resumes for applicant tracking systems (ATS). With smart suggestions and personalized feedback, it increases your chances of landing interviews by optimizing your resume structure against job descriptions and industry standards.

---

## 🎯 Key Features

- 🔍 **AI-Driven Resume Analysis**
- ✍️ **Personalized Suggestions**
- 📄 **PDF Resume Upload**
- 🧠 **Contextual Skill & Keyword Extraction**
- 📊 **Matching Score Display**
- 🤖 **Laravel + AI Integration**
- 📈 **Scalable & Modular Architecture**

---

## 🛠️ Built With

- **Laravel** (PHP Framework)
- **Blade** (View Templates)
- **MySQL** (Database)
- **JavaScript** (Frontend Interactions)
- **Python** (AI Resume Parsin, Machine Learning and Suggestions)
- **GROQ API** (for advanced text analysis and personalization)

---

## 📂 Project Structure

    ```bash
    atsblitz/
    ├── app/Http/Controllers/     # Laravel Controllers
    ├── app/Services/             # Business logic for resume matching
    ├── ai/                       # Python scripts for resume processing
    ├── resources/views/          # Blade Templates
    ├── routes/                   # Web and API Routes
    ├── public/                   # Public assets
    ├── database/migrations/      # Migration files
    ├── .env                      # Environment settings
    ├── composer.json             # PHP dependencies
    ├── package.json              # JS dependencies
    └── README.md                 # You're here!

## 🔄 Database Migrations
1. Run the following commands to set up your local database:

    ```bash
    php artisan migrate

-> Migrations handle creation of resume storage tables, analysis results, user sessions, etc.
