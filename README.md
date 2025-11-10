🚀 Interactive User Network - Frontend (React)

This is the React + TypeScript frontend for the Cybernauts Development Assignment. It consumes a FastAPI backend to provide a rich, interactive visualization of a user-hobby network.

🌎 Live Demo

Live Application (Vercel): [Link to your deployed Vercel app]

🌟 Features

Interactive Graph: Visualizes all users and friendships using React Flow.

Drag-and-Drop Linking: Create new friendships simply by dragging a connection from one user node to another.

Drag-and-Drop Hobbies: Add hobbies to users by dragging from the sidebar and dropping them onto any user node.

Dynamic Custom Nodes: Nodes automatically change their appearance based on their popularityScore:

LowScoreNode (Score <= 5)

HighScoreNode (Score > 5)

VeryHighScoreNode (Score > 10)

Live Score Updates: All scores and node appearances update in real-time after any change (e.g., adding a friend or a hobby).

Full User Management: A sidebar panel allows you to Create, Edit, and Delete users with form validation and confirmation.

Centralized State: Uses React Context and a useReducer hook to manage all graph data and loading states.

Notifications: Provides clear, non-intrusive feedback for all actions (create, link, delete, error) using react-hot-toast.

🛠️ Tech Stack

Library: React 18 (with TypeScript)

Build Tool: Vite

Graphing: React Flow

State Management: React Context + useReducer

API Client: Axios

Form Management: React Hook Form

Notifications: React Hot Toast

🚀 Setup and Installation (Local)

1. Prerequisite: Backend Server

This frontend requires the backend service to be running. Please follow its README.md to set it up.

By default, the backend must be running at http://localhost:8000.

2. Frontend Setup

Clone the repository:

git clone [Your-Frontend-Repo-URL]
cd cybernauts-frontend


Install dependencies:

npm install


Create your .env file:

Copy .env.example to a new file named .env.

Ensure the VITE_API_BASE_URL matches your running backend.

.env.example:

The URL of our FastAPI backend
VITE_API_BASE_URL=http://localhost:8000


Run the app:

npm run dev


The frontend will be running at http://localhost:5173 (or the next available port).
