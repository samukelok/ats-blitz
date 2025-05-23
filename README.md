# ⚡ ATSBlitz — AI-Powered Resume Analyzer

[🌐 Live Demo  →  atsblitz.bluenroll.co.za](https://atsblitz.bluenroll.co.za)

ATSBlitz is an AI-powered resume/CV analyser designed to help job seekers tailor their resumes for applicant tracking systems (ATS). With smart suggestions and personalised feedback, it increases your chances of landing interviews by optimizing your resume structure against job descriptions and industry standards.

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

> Migrations handle creation of resume storage tables, analysis results, user sessions, etc.

## 🚀 How to Run Locally
1. Clone the repo

    ```bash
    git clone https://github.com/YOUR_USERNAME/atsblitz.git
    cd atsblitz
2. Install dependencies

    ```bash
    composer install
    npm install

3. Configure .env



    ```bash
    cp .env.example .env
    php artisan key:generate

> Tip: Duplicate .env.example to .env and fill in your database credentials.

4. Migrate the database

    ```bash
    php artisan migrate

5. Serve the app

    ```bash
    php artisan serve

> Then visit http://localhost:8000 in your browser.

## 🤖 AI Analysis (Python Scripts)
- The ai/ directory includes Python scripts responsible for:

- Extracting skills and keywords

- Comparing job positions with resume

- Generating personalized feedback

## 🔐 Security & Privacy
- Uploaded resumes are not stored permanently, only the logs are.

- Data processing happens locally or securely through APIs.

- No third-party analytics or tracking.

## 📄 License
This project is open-source under the MIT License. You're free to use, modify, and distribute.

## ❤️ Contributing
We welcome PRs and issues! You can:

- Improve AI logic or resume suggestions

- Add new job targeting modes (e.g., industry-specific)

- Suggest UI/UX improvements

- Help localise or internationalise

## 👤 Created by
[@samukelok](https://github.com/samukelok)

Built for developers, job seekers, and hiring professionals.
