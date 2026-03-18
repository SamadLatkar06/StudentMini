# Smart Campus Issue Reporting

## MySQL Database - Full Setup

Run this complete SQL to create the database from scratch:

```sql
-- ============================================
-- Smart Campus - Complete MySQL Database
-- ============================================

CREATE DATABASE IF NOT EXISTS smartcampus;
USE smartcampus;

-- Drop existing tables if re-creating (optional - remove if keeping data)
-- DROP TABLE IF EXISTS issues;
-- DROP TABLE IF EXISTS users;

-- Users table (teacher_score: auto-increments +10 when teacher resolves an issue)
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100),
    email VARCHAR(100) UNIQUE,
    password VARCHAR(100),
    roll_no VARCHAR(50),
    role VARCHAR(50),
    department VARCHAR(50),
    teacher_score INT DEFAULT 0
);

-- Issues table (PC issues from students, assigned to repairers)
CREATE TABLE issues (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255),
    description TEXT,
    category VARCHAR(100),
    department VARCHAR(50),
    lab_name VARCHAR(100),
    pc_number INT,
    location VARCHAR(255),
    status VARCHAR(50) DEFAULT 'Submitted',
    reported_by INT,
    assigned_to INT,
    solved_by INT,
    score INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    resolved_at TIMESTAMP NULL,
    FOREIGN KEY (reported_by) REFERENCES users(id),
    FOREIGN KEY (assigned_to) REFERENCES users(id),
    FOREIGN KEY (solved_by) REFERENCES users(id)
);

-- Sample users
-- Student: login with roll_no only
INSERT INTO users (name, email, password, roll_no, role, department) VALUES
('Student1', NULL, NULL, 'S001', 'student', NULL);

-- Repairers (teachers): login with email + password
INSERT INTO users (name, email, password, roll_no, role, department) VALUES
('Repairer1', 'repairer1@gmail.com', '1234', NULL, 'teacher', 'AIML'),
('Repairer2', 'repairer2@gmail.com', '1234', NULL, 'teacher', 'AIDS');

-- Authority
INSERT INTO users (name, email, password, roll_no, role, department) VALUES
('Admin1', 'admin@gmail.com', '1234', NULL, 'authority', NULL);

-- Indexes
CREATE INDEX idx_issues_status ON issues(status);
CREATE INDEX idx_issues_department ON issues(department);
CREATE INDEX idx_issues_reported_by ON issues(reported_by);
CREATE INDEX idx_issues_solved_by ON issues(solved_by);
CREATE INDEX idx_users_roll_no ON users(roll_no);
CREATE INDEX idx_users_role ON users(role);
```

## Migration for Existing Database

If you already have the database, run these one by one (ignore errors for columns that exist):

```sql
USE smartcampus;

-- Add columns to users
ALTER TABLE users ADD COLUMN roll_no VARCHAR(50);
ALTER TABLE users ADD COLUMN department VARCHAR(50);

-- Update existing student
UPDATE users SET roll_no = 'S001' WHERE role = 'student' LIMIT 1;

-- Add repairers if not exists
INSERT INTO users (name, email, password, roll_no, role, department) 
SELECT 'Repairer1', 'repairer1@gmail.com', '1234', NULL, 'teacher', 'AIML'
WHERE NOT EXISTS (SELECT 1 FROM users WHERE email = 'repairer1@gmail.com');
INSERT INTO users (name, email, password, roll_no, role, department) 
SELECT 'Repairer2', 'repairer2@gmail.com', '1234', NULL, 'teacher', 'AIDS'
WHERE NOT EXISTS (SELECT 1 FROM users WHERE email = 'repairer2@gmail.com');

-- Add columns to issues
ALTER TABLE issues ADD COLUMN department VARCHAR(50);
ALTER TABLE issues ADD COLUMN lab_name VARCHAR(100);
ALTER TABLE issues ADD COLUMN pc_number INT;
ALTER TABLE issues ADD COLUMN reported_by INT;
ALTER TABLE issues ADD COLUMN assigned_to INT;
ALTER TABLE issues ADD COLUMN solved_by INT;
ALTER TABLE issues ADD COLUMN score INT;
ALTER TABLE issues ADD COLUMN resolved_at TIMESTAMP NULL;
ALTER TABLE users ADD COLUMN teacher_score INT DEFAULT 0;
```

## Test Logins

| Role | Login | Password |
|------|-------|----------|
| Student | Roll: S001 | - |
| Repairer (AIML) | repairer1@gmail.com | 1234 |
| Repairer (AIDS) | repairer2@gmail.com | 1234 |
| Authority | admin@gmail.com | 1234 |

## Flow

1. **Student** (roll no) → Choose Department (AIML/AIDS) → Lab map → Click PC → Report issue
2. **Repairer** (teacher) → Sees student-reported issues with Department & PC → Marks In Progress / Resolved (score +10 auto)
3. **Authority** → Sees issues, status, who solved → Bar chart of teacher scores (auto-updated)

## Run

```bash
pip install flask pymysql
python app.py
```
