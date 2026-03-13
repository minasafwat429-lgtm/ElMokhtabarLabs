# ElMokhtabar Labs

**ElMokhtabar Labs** is a full-stack web application designed to manage all operations of a medical laboratory.  
The project includes patient management, test tracking, results recording, staff roles, and billing, with a modern interactive frontend and a secure backend API.

---

## 1️⃣ Technologies & Stack

### Frontend (User Interface)
- **Languages:** HTML5, CSS3, JavaScript (Vanilla JS)
- **Frameworks/Libraries:**
  - **Three.js:** 3D interactive background for advanced visuals (`dna-scene.js`)
- **Design:** Glassmorphism cards with Dark Mode support
- **Responsive:** Fully responsive for all devices

### Backend (Server & API)
- **Language:** Python
- **Framework:** Flask (RESTful API)
- **Libraries / Dependencies:**
  - **Flask-SQLAlchemy:** ORM for database interactions
  - **PyMySQL:** MySQL database driver
  - **PyJWT:** Secure authentication using JSON Web Tokens
  - **Flask-CORS:** Enable secure frontend-backend communication
  - **Flask-Migrate:** Manage database migrations
  - **python-dotenv:** Load secret environment variables
  - **Werkzeug:** Core Flask dependency for HTTP request handling

### Database
- **System:** MySQL / MariaDB
- **Database Name:** ElMokhtabarLabs
- **Schema:** Relational database with foreign key relationships
- **Tables Include:** Patients, Branches, Doctors, Tests, Results, Equipment, Staff, Payments

---

## 2️⃣ Features

- Patient management (CRUD operations, medical history tracking)
- Test and sample management
- Results recording and automated report generation
- Staff role management with permissions (Doctors, Reception, Admin)
- Billing system with tracking of payments
- Secure authentication and authorization using JWT
- Responsive UI with 3D interactive visuals

---

## 3️⃣ Project Structure (Simplified)



ElMokhtabarLabs/
│
├── frontend/
│ ├── index.html
│ ├── css/
│ ├── js/
│ └── assets/
│
├── backend/
│ ├── app.py
│ ├── models.py
│ ├── routes/
│ ├── config.py
│ └── requirements.txt
│
├── database/
│ └── SQLQuery1.sql


---

## 4️⃣ How It Works

1. Frontend communicates with the Flask RESTful API.
2. Users log in using JWT authentication.
3. Data is stored in the MySQL database, supporting relational queries and reporting.
4. 3D interactive frontend enhances UX with modern visual effects.

---

## 5️⃣ Skills Demonstrated

- Full-Stack Web Development (Frontend + Backend)
- RESTful API development with Flask
- Database design & relational modeling (MySQL)
- Authentication & authorization (JWT)
- Frontend animations and 3D graphics using Three.js
- Environment configuration and dependency management (python-dotenv, requirements.txt)
- Responsive UI with modern Glassmorphism design

---

## 6️⃣ Disclaimer

This project is developed for **educational purposes** to demonstrate modern full-stack web development for medical laboratory management.
