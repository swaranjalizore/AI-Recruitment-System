CREATE DATABASE ai_recruitment_system;

USE ai_recruitment_system;

CREATE TABLE Candidate (
    candidate_id INT AUTO_INCREMENT PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    phone VARCHAR(15),
    education VARCHAR(100),
    skills TEXT,
    experience INT,
    location VARCHAR(100),
    resume_file VARCHAR(255),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE Recruiter (
    recruiter_id INT AUTO_INCREMENT PRIMARY KEY,
    company_name VARCHAR(200) NOT NULL,
    hr_name VARCHAR(200) NOT NULL,
    email VARCHAR(200) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    phone VARCHAR(15) NOT NULL UNIQUE,
    company_location VARCHAR(200),
    designation VARCHAR(200),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE Job (
    job_id INT AUTO_INCREMENT PRIMARY KEY,
    recruiter_id INT NOT NULL,
    job_title VARCHAR(200) NOT NULL,
    description TEXT NOT NULL,
    required_skills TEXT NOT NULL,
    experience_required INT NOT NULL,
    salary DECIMAL(10,2),
    location VARCHAR(100) NOT NULL,
    employment_type VARCHAR(50),
    openings INT NOT NULL,
    status VARCHAR(20),
    posted_date DATETIME DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (recruiter_id)
    REFERENCES Recruiter(recruiter_id)
);

CREATE TABLE application (
application_id INT AUTO_INCREMENT PRIMARY KEY,
candidate_id INT NOT NULL,
job_id INT NOT NULL,
application_date DATETIME DEFAULT CURRENT_TIMESTAMP,
status VARCHAR(30) NOT NULL,
match_score DECIMAL(5,2),
FOREIGN KEY (candidate_id)
REFERENCES candidate(candidate_id),
FOREIGN KEY (job_id)
REFERENCES job(job_id)
);

CREATE TABLE Admin (
    admin_id INT AUTO_INCREMENT PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    phone VARCHAR(15) UNIQUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);