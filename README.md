# Interactive User Network Backend (FastAPI)

This repository contains the backend service for the Interactive User Relationship and Hobby Network application. The service is implemented using **FastAPI** and exposes a structured API for managing users, their friendships, and associated hobby-based scoring.

## 1. Overview

The backend provides:

* CRUD operations for user management
* Bi-directional friendship linking and unlinking
* On-demand popularity score calculation based on social and hobby relationships
* A combined `/api/graph` endpoint supplying graph-ready data for visualization in the frontend
* Auto-generated OpenAPI documentation for ease of testing and integration

## 2. Live Deployment

* **API Base URL:** [https://interactive-user-relationship-hobby-u72g.onrender.com](https://interactive-user-relationship-hobby-u72g.onrender.com)
* **API Documentation:** [https://interactive-user-relationship-hobby-u72g.onrender.com/docs](https://interactive-user-relationship-hobby-u72g.onrender.com/docs)

## 3. Core Features

* **User and Relationship Management:** Create, retrieve, update, and delete user profiles and connections.
* **Popularity Scoring:** Each user receives a computed score derived from the count of direct friendships and shared hobby connections.
* **Data Consistency Controls:** The system prevents deletion operations that could compromise relational integrity.
* **Graph Aggregation Endpoint:** The `/api/graph` endpoint provides a unified structure of nodes and edges for the frontend.

## 4. Technology Stack

| Component  | Technology             |
| ---------- | ---------------------- |
| Framework  | FastAPI                |
| Database   | PostgreSQL (Async)     |
| ORM        | SQLAlchemy 2.0 (Async) |
| Validation | Pydantic               |
| Testing    | Pytest, HTTPX          |

## 5. API Endpoints (Summary)

| Method | Endpoint                 | Description                               |
| ------ | ------------------------ | ----------------------------------------- |
| GET    | `/api/users`             | Retrieve all users                        |
| POST   | `/api/users`             | Create a new user                         |
| GET    | `/api/users/{id}`        | Retrieve a specific user                  |
| PUT    | `/api/users/{id}`        | Update user details                       |
| DELETE | `/api/users/{id}`        | Delete a user (with integrity validation) |
| POST   | `/api/users/{id}/link`   | Create a friendship                       |
| DELETE | `/api/users/{id}/unlink` | Remove a friendship                       |
| GET    | `/api/graph`             | Retrieve all graph data for visualization |

## 6. Local Setup Instructions

1. **Clone the repository:**

```
git clone <repository-url>
cd backend
```

2. **Create and activate a virtual environment:**

```
python -m venv venv
# Windows
venv\Scripts\activate
# Mac/Linux
source venv/bin/activate
```

3. **Install dependencies:**

```
pip install -r requirements.txt
```

4. **Configure the environment:**
   Create a `.env` file based on the `.env.example` template and set:

```
DATABASE_URL=postgresql+asyncpg://USER:PASSWORD@HOST:PORT/DATABASE
```

5. **Run the development server:**

```
uvicorn app.main:app --reload --port 8000
```

## 7. Access During Development

* Local API Base: [http://localhost:8000](http://localhost:8000)
* Local API Documentation: [http://localhost:8000/docs](http://localhost:8000/docs)

## 8. Deployment Notes

Ensure that:

* The `DATABASE_URL` uses the async driver prefix `postgresql+asyncpg://`.
* Remote database access is configured with SSL (if hosting provider enforces it).

---

This documentation may be expanded based on project requirements, testing strategy, or additional integration details.
