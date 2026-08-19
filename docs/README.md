# Campus Event Pro – Enterprise Full-Stack Event Management System

![Campus Event Pro](https://images.unsplash.com/photo-1540575467063-178a50c2df87?w=1200&auto=format&fit=crop)

**Campus Event Pro** is a production-ready, enterprise-grade college event management platform with an integrated interactive internal calendar, QR code entry ticketing system, automated PDF certificate generation, and role-based dashboards for **Students**, **Teacher Coordinators**, and **Administrators**.

Designed specifically for **Java Full Stack Developer & Python Full Stack placement portfolios**.

---

## 🌟 Key Features & Functional Specifications

- **Interactive Internal Calendar**: Day, Week, Month, and Year calendar views with color-coded event categories, department filters, and instant event popups.
- **JWT Authentication & Role-Based Access Control (RBAC)**:
  - **Student**: Register for campus events, download QR entry tickets, view notifications, and download PDF certificates.
  - **Teacher Coordinator**: Dedicated portal showing assigned event, student registration directory with 10-digit mobile numbers, attendance toggle management, and Excel/CSV export.
  - **Admin**: Full event CRUD, Teacher Coordinator approval & rejection workflow, Event Coordinator assignment, user management, and system analytics.
- **Removed Public Admin Registration**: Public creation of admin accounts is permanently disabled. Admin accounts must be seeded or created directly in the database.
- **QR Code Ticket System**: Auto-generates unique entry tickets for attendees and instant gate validation.
- **Automated PDF Certificate Generator**: Generates official Certificates of Participation upon attendance verification.
- **Smart Catalog & Live Search**: Debounced live search, multi-filter by category & department, and seat availability progress bars.
- **Modern Glassmorphism UI/UX**: Built with custom CSS variables, light/dark theme persistence, responsive layouts, and smooth animations.

---

## 🛠️ Technology Stack

### Backend Options
1. **Java Spring Boot**: Java 17/21, Spring Security (JWT + BCrypt), Spring Data JPA, Hibernate, Maven.
2. **Python FastAPI**: Python 3.10+, FastAPI, SQLAlchemy ORM, Pydantic, Passlib, PyJWT, ReportLab, QRCode.

### Frontend
- HTML5, Vanilla CSS3 (Custom Glassmorphism Design System), JavaScript (ES6 Modules, Fetch API, Chart.js).

### Database
- **MySQL 8.0+** (Production Schema & Seed Data included in `database/schema.sql` and `database/sample_data.sql`).
- **SQLite 3** (Default local file-based database for zero-config startup).

---

## 📁 Repository Directory Structure

```text
CampusEventPro/
├── frontend/                  # Production Frontend Web Application
│   ├── index.html             # Landing Page & Featured Events
│   ├── events.html            # Smart Event Directory & Live Search
│   ├── calendar.html          # Interactive Internal Calendar View
│   ├── dashboard.html         # Student Dashboard
│   ├── teacher-dashboard.html # Teacher Coordinator Portal
│   ├── admin.html             # Admin Management Portal
│   ├── login.html             # Role-based Login Page
│   ├── register.html          # Student & Teacher Registration
│   ├── css/                   # Custom Glassmorphism Stylesheets
│   └── js/                    # Modular JavaScript Client Logic
├── backend/                   # Python FastAPI Backend Architecture
│   ├── main.py                # App entrypoint & DB seeding
│   ├── models.py              # SQLAlchemy ORM Models
│   ├── routes/                # Auth, Events, Admin, Registration endpoints
│   └── tests/                 # Automated Pytest Suite
├── backend-spring/            # Java Spring Boot Microservice Architecture
│   ├── pom.xml                # Maven Dependencies
│   └── src/main/java/com/campuseventpro/
│       ├── controller/        # REST Controllers (Auth, Events, Teachers)
│       ├── entity/            # JPA Entities (User, Event, TeacherCoordinator)
│       └── repository/        # Spring Data Repositories
├── database/                  # Database Scripts
│   ├── schema.sql             # MySQL Schema DDL
│   └── sample_data.sql        # Demo Accounts & Events Seed
└── docs/                      # Production Documentation
    ├── README.md
    └── API_DOCUMENTATION.md
```

---

## 🔑 Default Demo Credentials

On initial startup, default ready-to-use accounts are auto-seeded:

| Role | Email | Password | Employee / Roll No | Account Status |
| :--- | :--- | :--- | :--- | :--- |
| **Admin** | `admin@campuseventpro.edu` | `admin123` | ADM-001 | Active |
| **Teacher Coordinator** | `teacher@campuseventpro.edu` | `teacher123` | EMP-101 | Approved |
| **Teacher Coordinator** | `robert.lang@campuseventpro.edu` | `teacher123` | EMP-102 | Pending Approval |
| **Student** | `student@campuseventpro.edu` | `student123` | CSEIOT23045 | Active |

---

## 🚀 Local Quick Start Setup

### Option A: Python FastAPI Backend

```bash
# Install dependencies
pip install -r backend/requirements.txt

# Start backend server (Auto-seeds database and serves static frontend)
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
```
- Web Application: `http://127.0.0.1:8000/`
- OpenAPI Docs: `http://127.0.0.1:8000/docs`

### Option B: Java Spring Boot Backend

```bash
cd backend-spring
mvn spring-boot:run
```
- REST API Server: `http://localhost:8080/api`

---

## 📄 Cloud Deployment Guide

- **Frontend (Vercel)**: Configured via `vercel.json` for static SPA rewrites.
- **Backend (Render)**: Configured via `render.yaml` for instant container deployment.
- **Database (Railway / PlanetScale)**: Import `database/schema.sql` followed by `database/sample_data.sql`.
