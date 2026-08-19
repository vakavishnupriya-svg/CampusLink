# Campus Event Pro – Enterprise Full-Stack Event Management System

![Campus Event Pro](https://images.unsplash.com/photo-1540575467063-178a50c2df87?w=1200&auto=format&fit=crop)

**Campus Event Pro** is a production-ready, enterprise-grade college event management platform with an integrated interactive internal calendar built using **Python FastAPI** on the backend and **Vanilla HTML5, CSS3 (Glassmorphism), and JavaScript (ES6)** on the frontend.

Designed for Java Full Stack Developer placements and real-world portfolio showcases.

---

## 🌟 Key Features

- **Interactive Internal Calendar**: Day, Week, Month, and Year calendar views with color-coded event categories, department filters, and instant event popups.
- **JWT Authentication & Role-Based Access**:
  - **Student**: Join events, download QR entry tickets, view notifications, and download PDF certificates.
  - **Faculty**: Publish & edit events, manage student participants, scan QR codes for check-in.
  - **Admin**: System-wide user role management, analytics dashboard, and CSV data export.
- **QR Code Ticket System**: Auto-generates unique entry tickets for attendees and instant validation.
- **Automated PDF Certificate Generator**: Generates official Certificates of Participation upon attendance verification using ReportLab.
- **Smart Catalog & Live Search**: Debounced search, multi-filter by category & department, and seat availability progress bars.
- **Modern UI/UX**: Built with a sleek Glassmorphism design system, light/dark theme persistence, responsive layouts, and floating action cards.

---

## 🛠️ Technology Stack

- **Backend**: Python 3.14, FastAPI, SQLAlchemy ORM, SQLite database, Passlib (Bcrypt), PyJWT, ReportLab, QRCode, Pytest.
- **Frontend**: HTML5, Vanilla CSS3 (Custom Design System with Variables), JavaScript (Fetch API, ES6 Modules).
- **Deployment**: Render (FastAPI Backend) + Vercel (Static Frontend).

---

## 🚀 Quick Start & Local Setup

### 1. Backend Setup (FastAPI)

```bash
# Navigate to project root
cd CampusEventPro

# Install dependencies
pip install -r backend/requirements.txt

# Run server with Uvicorn (Auto-seeds database with demo users & events)
uvicorn backend.main:app --reload --port 8000
```

Backend OpenAPI Documentation will be available at: `http://localhost:8000/docs`

### 2. Frontend Setup

Simply open `frontend/index.html` in your browser or run a live server:

```bash
# Option A: Python HTTP Server
python -m http.server 5500
```
Then visit: `http://localhost:5500/frontend/index.html`

---

## 🔑 Default Demo Credentials

On initial startup, the database automatically seeds ready-to-use accounts:

| Role | Email | Password |
| :--- | :--- | :--- |
| **Student** | `student@campuseventpro.edu` | `student123` |
| **Faculty** | `faculty@campuseventpro.edu` | `faculty123` |
| **Admin** | `admin@campuseventpro.edu` | `admin123` |

---

## 🧪 Automated Testing

Run unit & endpoint integration tests:

```bash
pytest backend/tests/
```

---

## 📄 Deployment Configuration

- **Backend (Render)**: `render.yaml` pre-configured for instant deployment.
- **Frontend (Vercel)**: `vercel.json` pre-configured for static rewrites.

---

## 📜 License

MIT License - Open for educational and portfolio demonstration purposes.
