# Campus Event Pro – REST API Documentation

This document outlines the REST API specifications for **Campus Event Pro**.

---

## 🔑 Authentication APIs

### 1. User Login
- **URL**: `/api/auth/login`
- **Method**: `POST`
- **Content-Type**: `application/x-www-form-urlencoded`
- **Request Parameters**:
  - `username` (string, email address)
  - `password` (string)
- **Success Response (200 OK)**:
  ```json
  {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
    "user": {
      "id": 1,
      "full_name": "Dr. Arthur Pendelton",
      "email": "admin@campuseventpro.edu",
      "role": "admin",
      "department": "Administration"
    }
  }
  ```

### 2. Student Registration
- **URL**: `/api/auth/register`
- **Method**: `POST`
- **Request Body**:
  ```json
  {
    "full_name": "Jordan Lee",
    "email": "jordan@campuseventpro.edu",
    "password": "studentpassword123",
    "role": "student",
    "department": "Computer Science",
    "roll_number": "CS2026-088"
  }
  ```
- **Note**: Submitting `role: "admin"` returns `400 Bad Request`.

### 3. Teacher Coordinator Registration
- **URL**: `/api/auth/register-teacher`
- **Method**: `POST`
- **Request Body**:
  ```json
  {
    "name": "Prof. David Miller",
    "employee_id": "EMP-2026-009",
    "email": "david.miller@campuseventpro.edu",
    "phone": "9876543210",
    "department": "Information Technology",
    "password": "teacherpassword123",
    "confirm_password": "teacherpassword123"
  }
  ```
- **Success Response (201 Created)**:
  ```json
  {
    "success": true,
    "message": "Registration submitted successfully! Your account is pending Admin approval.",
    "status": "pending",
    "teacher_id": 3
  }
  ```

---

## 📅 Event Management APIs

### 1. List All Events
- **URL**: `/api/events`
- **Method**: `GET`
- **Query Parameters**: `search`, `category`, `department`, `status_filter`, `sort_by`
- **Sample Response (200 OK)**:
  ```json
  [
    {
      "id": 1,
      "title": "InnovateAI 2026 Hackathon & Symposium",
      "category": "Hackathon",
      "department": "Computer Science",
      "coordinator_id": 1,
      "coordinator_name": "Prof. Sarah Jenkins",
      "coordinator_department": "Computer Science",
      "venue": "Main Auditorium & Innovation Lab 3",
      "capacity": 250,
      "seats_taken": 184,
      "status": "approved"
    }
  ]
  ```

### 2. Create Event (Faculty & Admin)
- **URL**: `/api/events`
- **Method**: `POST`
- **Headers**: `Authorization: Bearer <token>`
- **Request Body**:
  ```json
  {
    "title": "AI Robotics Workshop",
    "description": "Hands-on robotics session.",
    "category": "Workshop",
    "department": "Computer Science",
    "venue": "Lab 3",
    "start_time": "2026-09-01T10:00:00Z",
    "end_time": "2026-09-01T16:00:00Z",
    "registration_deadline": "2026-08-31T23:59:59Z",
    "capacity": 100
  }
  ```

---

## 👨‍🏫 Admin & Teacher Management APIs

### 1. List Teacher Coordinators
- **URL**: `/api/admin/teachers`
- **Method**: `GET`
- **Headers**: `Authorization: Bearer <admin_token>`

### 2. Approve or Reject Teacher Coordinator
- **URL**: `/api/admin/teachers/{id}/status`
- **Method**: `PUT`
- **Headers**: `Authorization: Bearer <admin_token>`
- **Request Body**:
  ```json
  {
    "status": "approved"
  }
  ```

### 3. Assign Coordinator to Event
- **URL**: `/api/admin/events/{event_id}/assign-coordinator`
- **Method**: `PUT`
- **Headers**: `Authorization: Bearer <admin_token>`
- **Request Body**:
  ```json
  {
    "coordinator_id": 1
  }
  ```

---

## 🎟️ Registration & Attendance APIs

### 1. Student Event Registration
- **URL**: `/api/registrations`
- **Method**: `POST`
- **Request Body**:
  ```json
  {
    "eventId": 1,
    "fullName": "Alex Johnson",
    "rollNumber": "TEST2026-999",
    "email": "alex@campuseventpro.edu",
    "phone": "9876543210"
  }
  ```

### 2. Export Registrations to CSV
- **URL**: `/api/registrations/export?eventId=1`
- **Method**: `GET`
- **Response**: File Download (`text/csv`)
