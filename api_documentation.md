# Campus Event Pro - REST API Specification

## Base URL
- Local Development: `http://localhost:8000/api`
- Production Render: `https://campus-event-pro-backend.onrender.com/api`

---

## 1. Authentication Endpoints

### `POST /auth/register`
Creates a new user account (Student or Faculty).

**Request Body:**
```json
{
  "full_name": "Alex Rivera",
  "email": "alex@campuseventpro.edu",
  "password": "studentpassword123",
  "role": "student",
  "department": "Computer Science",
  "roll_number": "CS2026-089",
  "bio": "Tech enthusiast"
}
```

**Response (201 Created):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsIn...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "full_name": "Alex Rivera",
    "email": "alex@campuseventpro.edu",
    "role": "student",
    "department": "Computer Science",
    "is_active": true,
    "created_at": "2026-08-18T12:00:00"
  }
}
```

### `POST /auth/login`
OAuth2 form endpoint for authentication.

**Form Data:** `username` (email), `password`

---

## 2. Events Endpoints

### `GET /events`
Retrieves filtered and sorted events catalog.

**Query Parameters:**
- `search` (string)
- `category` (string)
- `department` (string)
- `sort_by` (`newest`, `popular`, `closest`)

### `POST /events` *(Faculty / Admin Only)*
Creates a new campus event on the calendar.

---

## 3. Calendar Endpoints

### `GET /calendar/events`
Returns list of events formatted for calendar rendering.

---

## 4. Attendance & QR Endpoints

### `POST /attendance/checkin` *(Faculty / Admin Only)*
Scans student QR ticket token, records attendance, and automatically triggers PDF certificate generation.

---

## 5. Certificates Endpoints

### `GET /certificates`
Returns all certificates earned by current user.

---

## 6. Admin Analytics Endpoints

### `GET /admin/analytics` *(Admin Only)*
Returns system statistics, attendance rate, monthly trends, and user distribution.
