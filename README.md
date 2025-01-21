# Learning Management System (LMS) with Django

## Project Overview
The **Learning Management System (LMS)** is a web-based application built using Django and MySQL. It is designed to facilitate online education by enabling course management, student enrollment, progress tracking, and more. The system is role-based, supporting functionalities for students, instructors, and administrators.

## Features

### General
- Role-based access control (students, instructors, administrators).
- User-friendly interface with consistent HTML class names across templates.
- Dynamic progress tracking and saving as students interact with the learning platform.

### For Students
- Enroll in courses and track progress.
- Access course materials, including videos, assignments, and quizzes.
- View grades and performance reports.

### For Instructors
- Upload and manage courses, lessons, assignments, and quizzes.
- Monitor student performance and provide feedback.

### For Administrators
- Manage users, roles, and permissions.
- Oversee courses and content.
- Generate reports on system usage and performance metrics.

### Additional Highlights
- Robust database schema with:
  - **Course** model including fields for title, description, objectives, difficulty level, instructors, students, price, and timestamps.
  - ManyToMany relationships between instructors and courses, with student enrollments managed via an `Enrollment` through model.
- Secure payment integration using **Paystack** for course purchases.
- Soft delete functionality for safe data removal.
- Role-specific dashboards for personalized experiences.
- Backend-first handling of discounts, taxes, and shipping costs.

## Tech Stack

### Backend
- **Django**: Web framework
- **MySQL**: Database
- **Paystack**: Payment gateway

### Frontend
- HTML5, CSS3, JavaScript
- Bootstrap (for responsive design)

### Deployment
- currently github

## Installation and Setup

### Prerequisites
- Python 3.8+
- Django 4.0+
- MySQL server

### Steps
1. Clone the repository:
   ```bash
   git clone git@github.com:OfficialEcho95/LMSwithdjango.git
   cd LMSwithdjango
   ```

2. Create and activate a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up the database:
   - Update `DATABASES` in `settings.py` with your MySQL credentials.
   - Apply migrations:
     ```bash
     python manage.py migrate
     ```

5. Collect static files:
   ```bash
   python manage.py collectstatic
   ```

6. Run the development server:
   ```bash
   python manage.py runserver
   ```

7. Open the application in your browser:
   ```
   http://127.0.0.1:8000
   ```

## Future Enhancements
- Integration with Django Channels for real-time notifications.
- Advanced analytics dashboard for administrators.
- Support for live classes and webinars.

## License
This project is licensed under the MIT License. See the `LICENSE` file for details.

## Contributing
Contributions are welcome! Please fork the repository, create a new branch, and submit a pull request with detailed explanations.

## Contact
For inquiries or support, reach out to:
- **Email**: emmanuelchukwu1968@gmail.com
- **GitHub**: https://github.com/OfficialEcho95/
