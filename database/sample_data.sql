-- Campus Event Pro Sample Seed Data
USE campus_event_pro;

-- Insert Initial Users (Passwords hashed using BCrypt: admin123, faculty123, student123)
INSERT INTO users (id, full_name, email, hashed_password, role, department, roll_number, bio) VALUES
(1, 'Dr. Arthur Pendelton', 'admin@campuseventpro.edu', '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeg6Lruj3vjPGga31lW', 'admin', 'Administration', 'ADM-001', 'Chief Administrator & Campus Event Director'),
(2, 'Prof. Sarah Jenkins', 'faculty@campuseventpro.edu', '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeg6Lruj3vjPGga31lW', 'faculty', 'Computer Science', 'FAC-102', 'Senior Associate Professor of AI & Robotics'),
(3, 'Alex Rivera', 'student@campuseventpro.edu', '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeg6Lruj3vjPGga31lW', 'student', 'Computer Science', 'CSEIOT23045', '3rd Year Computer Science Undergrad | Tech Lead at Coding Club');

-- Insert Teacher Coordinators
INSERT INTO teacher_coordinators (id, name, employee_id, email, phone, department, password_hash, status) VALUES
(1, 'Prof. Sarah Jenkins', 'EMP-101', 'teacher@campuseventpro.edu', '9876543210', 'Computer Science', '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeg6Lruj3vjPGga31lW', 'approved'),
(2, 'Dr. Robert Lang', 'EMP-102', 'robert.lang@campuseventpro.edu', '9876543211', 'Information Technology', '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeg6Lruj3vjPGga31lW', 'pending');

-- Insert Sample Campus Events
INSERT INTO events (id, title, description, category, department, organizer_id, coordinator_id, venue, start_time, end_time, capacity, seats_taken, registration_deadline, banner_url, status, is_featured, speaker_name, speaker_title) VALUES
(1, 'InnovateAI 2026 Hackathon & Symposium', 'Join 500+ student developers for an intense 36-hour hackathon focused on Generative AI, Autonomous Robotics, and Sustainable Tech. Cash prizes up to $10,000!', 'Hackathon', 'Computer Science', 2, 1, 'Main Auditorium & Innovation Lab 3', DATE_ADD(NOW(), INTERVAL 2 DAY), DATE_ADD(NOW(), INTERVAL 3 DAY), 250, 184, DATE_ADD(NOW(), INTERVAL 1 DAY), 'https://images.unsplash.com/photo-1504384308090-c894fdcc538d?w=1000&auto=format&fit=crop', 'approved', TRUE, 'Dr. Marcus Vance', 'VP of AI Research at OpenAI'),
(2, 'Annual Spring Cultural Fest - Rhythm & Harmony', 'The largest cultural festival of the year! Live battle of the bands, classical dance showcases, theatrical performances, and street food stalls.', 'Cultural', 'Cultural Club', 1, NULL, 'Open Air Amphitheatre', DATE_ADD(NOW(), INTERVAL 5 DAY), DATE_ADD(NOW(), INTERVAL 6 DAY), 1000, 620, DATE_ADD(NOW(), INTERVAL 4 DAY), 'https://images.unsplash.com/photo-1492684223066-81342ee5ff30?w=1000&auto=format&fit=crop', 'approved', TRUE, 'Elena Rostova', 'Grammy Award Winning Violinist'),
(3, 'Global Tech Career Fair & Placement Drive 2026', 'Meet recruiters from over 60 Fortune 500 tech companies and high-growth startups. On-spot interview rooms, resume review booths, and networking lounges.', 'Placement', 'Placement Cell', 2, NULL, 'University Student Center - Level 2', DATE_ADD(NOW(), INTERVAL 8 DAY), DATE_ADD(NOW(), INTERVAL 8 DAY), 500, 340, DATE_ADD(NOW(), INTERVAL 7 DAY), 'https://images.unsplash.com/photo-1511578314322-379afb476865?w=1000&auto=format&fit=crop', 'approved', FALSE, 'David Sterling', 'Head of Global Talent Acquisition'),
(4, 'Inter-Departmental Athletics & Football Tournament', 'Cheer for your department! Men''s and Women''s football league, sprint track, high jump, and table tennis championship.', 'Sports', 'Physical Education', 1, NULL, 'Central Sports Complex Field A', DATE_ADD(NOW(), INTERVAL 12 DAY), DATE_ADD(NOW(), INTERVAL 14 DAY), 300, 190, DATE_ADD(NOW(), INTERVAL 10 DAY), 'https://images.unsplash.com/photo-1461896836934-ffe607ba8211?w=1000&auto=format&fit=crop', 'approved', FALSE, 'Coach Ryan Miller', 'National Athletics Coach'),
(5, 'Hands-on Workshop: Full-Stack Web Dev with Fast-API & Cloud', 'Master modern backend microservices, async databases, Docker containerization, and serverless deployment workflows.', 'Workshop', 'Information Technology', 2, 2, 'Computer Center - Lab 4', DATE_ADD(NOW(), INTERVAL 1 DAY), DATE_ADD(NOW(), INTERVAL 1 DAY), 60, 45, DATE_ADD(NOW(), INTERVAL 12 HOUR), 'https://images.unsplash.com/photo-1531403009284-440f080d1e12?w=1000&auto=format&fit=crop', 'approved', TRUE, 'Prof. Sarah Jenkins', 'Senior Faculty IT');

-- Link Teacher assigned_event_id
UPDATE teacher_coordinators SET assigned_event_id = 1 WHERE id = 1;
UPDATE teacher_coordinators SET assigned_event_id = 5 WHERE id = 2;
