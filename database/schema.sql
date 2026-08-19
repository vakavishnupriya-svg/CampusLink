-- Campus Event Pro Database Schema
-- Compatible with MySQL 8.0+ and SQLite

CREATE DATABASE IF NOT EXISTS campus_event_pro;
USE campus_event_pro;

-- 1. Users Table
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    hashed_password VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL DEFAULT 'student',
    department VARCHAR(100) DEFAULT 'Computer Science',
    roll_number VARCHAR(50) NULL,
    phone VARCHAR(20) DEFAULT '+91 9876543210',
    avatar_url VARCHAR(255) NULL,
    bio TEXT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 2. Teacher Coordinators Table
CREATE TABLE IF NOT EXISTS teacher_coordinators (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    employee_id VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(100) NOT NULL UNIQUE,
    phone VARCHAR(20) NOT NULL,
    department VARCHAR(100) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    assigned_event_id INT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 3. Events Table
CREATE TABLE IF NOT EXISTS events (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    description TEXT NOT NULL,
    category VARCHAR(50) NOT NULL,
    department VARCHAR(100) NOT NULL,
    organizer_id INT NOT NULL,
    coordinator_id INT NULL,
    venue VARCHAR(200) NOT NULL,
    start_time DATETIME NOT NULL,
    end_time DATETIME NOT NULL,
    capacity INT DEFAULT 100,
    seats_taken INT DEFAULT 0,
    registration_deadline DATETIME NOT NULL,
    banner_url VARCHAR(500) NULL,
    status VARCHAR(20) DEFAULT 'approved',
    is_featured BOOLEAN DEFAULT FALSE,
    is_paid BOOLEAN DEFAULT FALSE,
    ticket_price DOUBLE DEFAULT 0.0,
    speaker_name VARCHAR(100) NULL,
    speaker_title VARCHAR(100) NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (organizer_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (coordinator_id) REFERENCES teacher_coordinators(id) ON DELETE SET NULL
);

-- Foreign key link back to events for teacher_coordinators
ALTER TABLE teacher_coordinators 
ADD CONSTRAINT fk_teacher_assigned_event 
FOREIGN KEY (assigned_event_id) REFERENCES events(id) ON DELETE SET NULL;

-- 4. Event Registrations Table
CREATE TABLE IF NOT EXISTS event_registrations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    registration_id VARCHAR(100) NOT NULL UNIQUE,
    user_id INT NULL,
    event_id INT NOT NULL,
    event_name VARCHAR(200) NULL,
    full_name VARCHAR(100) NOT NULL,
    roll_no VARCHAR(50) NOT NULL,
    email VARCHAR(100) NOT NULL,
    phone VARCHAR(20) NULL,
    department VARCHAR(100) NULL,
    year VARCHAR(20) DEFAULT '3rd Year',
    section VARCHAR(20) DEFAULT 'Sec A',
    status VARCHAR(20) DEFAULT 'approved',
    attendance INT DEFAULT 0,
    registered_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    qr_code_token VARCHAR(100) NOT NULL UNIQUE,
    qr_code_url VARCHAR(500) NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL,
    FOREIGN KEY (event_id) REFERENCES events(id) ON DELETE CASCADE
);

-- 5. Bookmarks Table
CREATE TABLE IF NOT EXISTS bookmarks (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    event_id INT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (event_id) REFERENCES events(id) ON DELETE CASCADE
);

-- 6. Attendance Table
CREATE TABLE IF NOT EXISTS attendance (
    id INT AUTO_INCREMENT PRIMARY KEY,
    event_id INT NOT NULL,
    user_id INT NOT NULL,
    checked_in_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    method VARCHAR(20) DEFAULT 'qr',
    FOREIGN KEY (event_id) REFERENCES events(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- 7. Certificates Table
CREATE TABLE IF NOT EXISTS certificates (
    id INT AUTO_INCREMENT PRIMARY KEY,
    certificate_number VARCHAR(100) NOT NULL UNIQUE,
    user_id INT NOT NULL,
    event_id INT NOT NULL,
    issued_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    pdf_path VARCHAR(500) NOT NULL,
    verification_url VARCHAR(500) NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (event_id) REFERENCES events(id) ON DELETE CASCADE
);

-- 8. Notifications Table
CREATE TABLE IF NOT EXISTS notifications (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    title VARCHAR(150) NOT NULL,
    message TEXT NOT NULL,
    type VARCHAR(50) DEFAULT 'info',
    is_read BOOLEAN DEFAULT FALSE,
    link VARCHAR(255) NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
