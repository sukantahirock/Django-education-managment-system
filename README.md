# Django-education-managment-system


---

# 🎓 Django Role-Based API System (Admin, Teacher, Student)

This project is a Django REST Framework (DRF)-based backend system that supports three types of users — **Admin**, **Teacher**, and **Student** — each with specific permissions and REST APIs. JWT authentication is implemented using `djangorestframework-simplejwt`.

---

## 🚀 Features

### 🔐 Authentication

* JWT-based authentication via `djangorestframework-simplejwt`
* Custom user model with roles: `admin`, `teacher`, `student`

### 👤 Role-Based Permissions

* **Admin**:

  * Create, update, delete users (of any role)
  * View all courses and enrollments
* **Teacher**:

  * Create, update, delete own courses
  * View enrollments in their own courses
* **Student**:

  * View available courses
  * Enroll in courses (max 5 active)
  * View own enrollments

---

## 🏗️ Project Structure

```
myproject/
├── manage.py
├── myproject/           # Main Django project
│   └── settings.py
├── restapi/             # DRF app
│   ├── models.py
│   ├── views.py
│   ├── serializers.py
│   ├── permissions.py
│   ├── urls.py
└── requirements.txt
```

---

## ⚙️ Installation

1. **Clone the repository**

```bash
git clone https://github.com/yourusername/role-based-api-django.git
cd role-based-api-django
```

2. **Create a virtual environment and activate it**

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**

```bash
pip install -r requirements.txt
```

4. **Apply migrations**

```bash
python manage.py makemigrations
python manage.py migrate
```

5. **Create a superuser**

```bash
python manage.py createsuperuser
```

6. **Run the development server**

```bash
python manage.py runserver
```

---

## 🔐 JWT Authentication Endpoints

| Endpoint              | Method | Description                  |
| --------------------- | ------ | ---------------------------- |
| `/api/token/`         | POST   | Get access and refresh token |
| `/api/token/refresh/` | POST   | Refresh access token         |

---

## 📡 API Endpoints Overview

> Requires JWT token in `Authorization: Bearer <token>` header

### Admin APIs

| Endpoint            | Method | Description          |
| ------------------- | ------ | -------------------- |
| `/api/users/`       | POST   | Create user          |
| `/api/users/<id>/`  | PUT    | Update user          |
| `/api/users/<id>/`  | DELETE | Delete user          |
| `/api/courses/`     | GET    | View all courses     |
| `/api/enrollments/` | GET    | View all enrollments |

### Teacher APIs

| Endpoint             | Method | Description                     |
| -------------------- | ------ | ------------------------------- |
| `/api/courses/`      | POST   | Create course                   |
| `/api/courses/<id>/` | PUT    | Update own course               |
| `/api/courses/<id>/` | DELETE | Delete own course               |
| `/api/enrollments/`  | GET    | View enrollments in own courses |

### Student APIs

| Endpoint            | Method | Description                |
| ------------------- | ------ | -------------------------- |
| `/api/courses/`     | GET    | View available courses     |
| `/api/enrollments/` | POST   | Enroll in course (limit 5) |
| `/api/enrollments/` | GET    | View own enrollments       |

---

## ✅ Tech Stack

* Python 3.9+
* Django 4.x
* Django REST Framework
* Simple JWT
* SQLite (default, but you can configure PostgreSQL)

---

## 🔒 Permissions

All role-based access is enforced using custom `permissions.py` logic.

---


---

