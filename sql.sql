CREATE TABLE course (
  id INT AUTO_INCREMENT PRIMARY KEY,
  course_code VARCHAR(16) NOT NULL UNIQUE,
  course_title VARCHAR(255) NOT NULL,
  credits TINYINT NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE rooms (
  id INT AUTO_INCREMENT PRIMARY KEY,
  room_code VARCHAR(32) NOT NULL UNIQUE,
  capacity INT NOT NULL,
  building VARCHAR(128),
  floor SMALLINT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE students (
  id INT AUTO_INCREMENT PRIMARY KEY,
  roll_no VARCHAR(32) NOT NULL UNIQUE,
  name VARCHAR(255) NOT NULL,
  department VARCHAR(64),
  year TINYINT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE invigilators (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(255) NOT NULL,
  employee_no VARCHAR(64) NOT NULL UNIQUE,
  dept VARCHAR(128),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Exams reference course.course_code (course_code is UNIQUE) and also have their own numeric PK id
CREATE TABLE exams (
  id INT AUTO_INCREMENT PRIMARY KEY,
  course_code VARCHAR(16) NOT NULL,
  course_title VARCHAR(255) NOT NULL,
  exam_date DATE NOT NULL,
  start_time TIME,
  end_time TIME,
  venue_note VARCHAR(255),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_exams_course_code FOREIGN KEY (course_code) REFERENCES course(course_code) ON UPDATE CASCADE ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Junction and assignment tables
CREATE TABLE student_exam (
  id INT AUTO_INCREMENT PRIMARY KEY,
  student_id INT NOT NULL,
  exam_id INT NOT NULL,
  status ENUM('registered','absent','completed','cancelled') DEFAULT 'registered',
  registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT uq_student_exam UNIQUE (student_id, exam_id),
  CONSTRAINT fk_studentexam_student FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT fk_studentexam_exam FOREIGN KEY (exam_id) REFERENCES exams(id) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE seat_assignment (
  id INT AUTO_INCREMENT PRIMARY KEY,
  exam_id INT NOT NULL,
  room_id INT NOT NULL,
  student_id INT NOT NULL,
  seat_number INT NOT NULL,
  assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT uq_exam_room_seat UNIQUE (exam_id, room_id, seat_number),
  CONSTRAINT uq_exam_student UNIQUE (exam_id, student_id),
  CONSTRAINT fk_seat_exam FOREIGN KEY (exam_id) REFERENCES exams(id) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT fk_seat_room FOREIGN KEY (room_id) REFERENCES rooms(id) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT fk_seat_student FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE invigilator_availability (
  id INT AUTO_INCREMENT PRIMARY KEY,
  invigilator_id INT NOT NULL,
  date DATE NOT NULL,
  start_time TIME,
  end_time TIME,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_avail_invigilator FOREIGN KEY (invigilator_id) REFERENCES invigilators(id) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE invigilation_assignment (
  id INT AUTO_INCREMENT PRIMARY KEY,
  exam_id INT NOT NULL,
  room_id INT NOT NULL,
  invigilator_id INT NOT NULL,
  role VARCHAR(64),
  assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_invig_exam FOREIGN KEY (exam_id) REFERENCES exams(id) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT fk_invig_room FOREIGN KEY (room_id) REFERENCES rooms(id) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT fk_invig_invigilator FOREIGN KEY (invigilator_id) REFERENCES invigilators(id) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT uq_invig_assignment UNIQUE (exam_id, room_id, invigilator_id, role)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


INSERT INTO course (course_code, course_title, credits) VALUES
('CS101', 'Introduction to Programming', 3),
('CS102', 'Data Structures and Algorithms', 4),
('CS201', 'Database Management Systems', 4),
('CS202', 'Operating Systems', 4),
('CS210', 'Computer Networks', 4),
('CS220', 'Object Oriented Programming', 3),
('MA101', 'Calculus I', 3),
('MA102', 'Linear Algebra', 3),
('MA201', 'Discrete Mathematics', 3),
('PH101', 'Engineering Physics', 3),
('CH101', 'Engineering Chemistry', 3),
('EE101', 'Basic Electrical Engineering', 3),
('EE201', 'Digital Electronics', 4);  -- added so exams FK won't fail

-- Insert rooms
INSERT INTO rooms (room_code, capacity, building, floor) VALUES
('B1-101', 60, 'Block 1', 1),
('B1-102', 40, 'Block 1', 1),
('B2-201', 30, 'Block 2', 2),
('B3-301', 50, 'Block 3', 3);

-- Insert exams (course_code must exist in course)
INSERT INTO exams (course_code, course_title, exam_date, start_time, end_time, venue_note) VALUES
('CS101', 'Introduction to Programming', '2025-12-01', '09:00', '12:00', 'Morning Slot'),
('MA101', 'Calculus I', '2025-12-02', '13:00', '16:00', 'Afternoon Slot'),
('PH101', 'Physics I', '2025-12-03', '10:00', '13:00', 'Main Hall'),
('EE201', 'Digital Electronics', '2025-12-04', '14:00', '17:00', 'Block 2');

-- Insert students
INSERT INTO students (roll_no, name, department, year) VALUES
('22CS001', 'Aarav Sharma', 'CSE', 2),
('22CS002', 'Ishaan Verma', 'CSE', 2),
('22EC001', 'Riya Singh', 'ECE', 2),
('22EC002', 'Neha Mehta', 'ECE', 3),
('22EE001', 'Ankit Gupta', 'EEE', 1),
('22ME001', 'Sarthak Yadav', 'Mechanical', 2);

-- student_exam: using numeric student_id and exam_id (auto-incremented)
INSERT INTO student_exam (student_id, exam_id, status) VALUES
(1, 1, 'registered'),
(2, 1, 'registered'),
(3, 1, 'registered'),
(4, 2, 'registered'),
(1, 2, 'registered'),
(5, 3, 'registered'),
(6, 4, 'registered');

-- seat assignments
INSERT INTO seat_assignment (exam_id, room_id, student_id, seat_number) VALUES
(1, 1, 1, 1),
(1, 1, 2, 2),
(1, 1, 3, 3),
(2, 2, 4, 1),
(2, 2, 1, 2);

-- invigilators
INSERT INTO invigilators (name, employee_no, dept) VALUES
('Prof. Manish Kumar', 'EMP001', 'CSE'),
('Prof. Shalini Rao', 'EMP002', 'ECE'),
('Dr. Vinod Khanna', 'EMP003', 'Physics'),
('Prof. Pooja Sinha', 'EMP004', 'Mathematics');

-- invigilator availability
INSERT INTO invigilator_availability (invigilator_id, date, start_time, end_time) VALUES
(1, '2025-12-01', '08:00', '13:00'),
(2, '2025-12-02', '12:00', '17:00'),
(3, '2025-12-03', '09:00', '14:00'),
(4, '2025-12-04', '13:00', '18:00');

-- invigilation assignments
INSERT INTO invigilation_assignment (exam_id, room_id, invigilator_id, role) VALUES
(1, 1, 1, 'chief'),
(1, 1, 2, 'invigilator'),
(2, 2, 4, 'chief'),
(3, 3, 3, 'invigilator');