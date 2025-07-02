# MoreHealth AI GenAI 
MoreHealth is an AI-driven health assistant platform where users interact with an artificial intelligences genAI to describe symptoms and receive personalized treatment recommendations. The system leverages custom-built machine learning models to analyze user input, suggest evidence-based remedies, and offer additional AI-powered health services such as lifestyle advice, medication info, and preventive care tips.

## High-Level Architecture

* **Backend**: Django (5) with PostgreSQL database, using Django REST Framework for API endpoints
* **Authentication**: JWT-based security with email verification
* **Communication**: Real-time chat system (Socket.IO) and community forum

---

## Requirements & Technologies

### Backend Stack

* **Python 3.13**
* **Django 5**
* **Django REST Framework**
* **PostgreSQL**
* **Additional Packages**:

  * `django-cors-headers` for CORS management
  * `Pillow` for image processing
  * `python-dotenv` for environment variables
  * `psycopg2-binary` for PostgreSQL adapter
  * `gunicorn` for production WSGI


### Development Tooling

* **Python virtualenv**
* **pip / virtualenv**
* **PostgreSQL client**


---

## Installation & Running Instructions

1. **Clone the Repository**

   ```bash
   git clone https://github.com/HasanOmarHasan/MoreHealth.git
   cd MoreHealth
   ```

2. **Backend Setup**

   ```bash
   cd backend
   python3 -m venv venv
   source venv/bin/activate    # Linux/macOS
   venv\Scripts\activate     # Windows
   pip install -r requirements.txt
   ```

   * Create a `.env` in the `backend/` directory with:

     ```ini
     DATABASE_URL=postgres://USER:PASSWORD@localhost:5432/morehealth_db
     JWT_SECRET=your_jwt_secret_key
     EMAIL_HOST=smtp.gmail.com
     EMAIL_PORT=587
     EMAIL_HOST_USER=your_email@gmail.com
     EMAIL_HOST_PASSWORD=your_app_password
     ```
   * Apply migrations and start server:

     ```bash
     python manage.py migrate
     python manage.py runserver
     ```



4. **Access the Application**

   * API: `http://localhost:8000/`
   * sign up as doctor : `http://127.0.0.1:8000/auth/signup-doctor`
   * sign up as regleur user : `http://127.0.0.1:8000/auth/signup`
   * login : `http://127.0.0.1:8000//auth/login`
   * test token : ` http://127.0.0.1:8000/auth/test-token`
     

---

## Key Features & Workflow

### Authentication & Authorization

* **User Registration**: Registration with email verification via Google SMTP
* **Password Management**: Forgot password and secure reset tokens
* **JWT Authentication**: Access and refresh tokens to secure API endpoints 
* **Protected Endpoints**: Role-based access control for sensitive resources

### User Profile Management

* **Profile Editing**: Update personal details and preferences
* **Account Deletion**: Secure removal with confirmation workflow

### Social & Notifications

* **Friend System**: Send, accept, or decline friend requests
* **Real-time Alerts**: Socket.IO-powered notifications for new requests and activities
* **Activity Feed**: View recent friend activities and system messages

### Chat Module

* **1:1 Messaging**: Secure real-time chat between users and doctors
* **Message History**: Persistent storage of conversations with timestamps
* **Online Status**: Presence indicators for active users

### Community Forum

* **Discussion Groups**: Create and join topic-based communities
* **Q\&A System**: Post questions with threaded replies and comments
* **Content Moderation**: Edit or delete your own posts and replies
* **Advanced Search**: Filter , popularity, or recency , can search by groub name , mamber name , creater , username , own groub , describtion and so in 
* **Edit Tracking**: Visual indicators showing when content was last modified

### Admin Verification:

* Admin dashboard for verifying doctor profiles
* Review submitted credentials and certifications
* Approve or reject doctor accounts based on verification status
* Role assignment for verified doctors with elevated permissions


