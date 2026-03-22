# 💊 Medical Appointment System API

A robust, RESTful backend API built with **FastAPI** to manage doctor availability, patient appointments, and consultation workflows. This project simulates a real-world healthcare scheduling system with dynamic pricing, complex validations, and appointment lifecycle management.

## 🚀 Features

* **Advanced Routing & CRUD:** Full Create, Read, Update, and Delete capabilities for doctors and appointments, following strict REST principles and FastAPI routing rules.
* **Business Logic & Dynamic Pricing:** Calculates consultation fees dynamically based on appointment type (in-person, video, emergency) and applies conditional discounts (e.g., senior citizen discounts).
* **State Management:** Automatically toggles a doctor's availability (`is_available`) when an appointment is booked or canceled.
* **Smart Search & Filtering:** Includes dedicated endpoints to search by keyword, filter by multiple criteria (specialization, fee, experience), sort dynamically, and paginate results.
* **Combined Browse Endpoint:** A powerful `/browse` route that combines filtering, sorting, and pagination in a single query hierarchy.
* **Data Validation:** Utilizes strict Pydantic models to ensure all incoming data meets business requirements (e.g., minimum string lengths, minimum values for fees/quantities).

## 🛠️ Tech Stack

* **Python 3.9+**
* **FastAPI** (Web framework)
* **Pydantic** (Data validation)
* **Uvicorn** (ASGI server)

# Start the FastAPI server:

uvicorn main:app --reload


# Access the API Documentation:
Open your browser and navigate to the interactive Swagger UI to test the endpoints:
👉 http://127.0.0.1:8000/docs 

# 🧩 Data Models (Pydantic)
The application uses strict Pydantic models for data validation:

AppointmentRequest: Validates incoming appointment bookings (patient name, doctor ID, date, reason, appointment type, and senior citizen status).

NewDoctor: Validates the creation of a new doctor profile (name, specialization, fee, experience years, and availability).

# 🛠️ Helper Functions
Core business logic is abstracted into plain Python helper functions:

find_doctor(doctor_id): Safely queries the mock database for a specific doctor.

calculate_fee(base_fee, appointment_type, senior_citizen): Calculates dynamic pricing. Applies modifiers for video (80%) or emergency (150%) consultations, followed by an optional 15% senior citizen discount.

filter_doctors_logic(...): Handles complex, multi-parameter filtering using is not None checks.

# 🔀 API Endpoints Reference
## 🏥 Doctors (Fixed Routes)

GET / - Welcome message.

GET /doctors - Retrieve all doctors.


GET /doctors/summary - Get aggregated statistics (most experienced, cheapest fee, specialization counts).

GET /doctors/filter - Filter doctors by specialization, max fee, min experience, or availability status.


GET /doctors/search - Search doctors by keyword (matches name or specialization).


GET /doctors/sort - Sort doctors dynamically by fee, name, or experience.


GET /doctors/page - Paginate the doctors list.


GET /doctors/browse - Combined Endpoint: Filter, sort, and paginate in a single request.

👨‍⚕️ Doctors (Variable Routes)

GET /doctors/{doctor_id} - Retrieve a specific doctor by ID.


POST /doctors - Add a new doctor to the system.


PUT /doctors/{doctor_id} - Update a doctor's fee or availability.


DELETE /doctors/{doctor_id} - Delete a doctor (Blocked if the doctor has active appointments).

## 📅 Appointments
GET /appointments - Retrieve all appointments.

GET /appointments/active - Retrieve only scheduled or confirmed appointments.

GET /appointments/search - Search appointments by patient name.

GET /appointments/sort - Sort appointments by fee or date.

GET /appointments/page - Paginate the appointments list.

GET /appointments/by-doctor/{doctor_id} - View appointment history for a specific doctor.

POST /appointments - Book a new appointment. (Automatically calculates fees and marks the doctor as unavailable).

## 🔄 Multi-Step Workflow (Appointment Lifecycle)
POST /appointments/{appointment_id}/confirm - Changes status to confirmed.

POST /appointments/{appointment_id}/complete - Changes status to completed.

POST /appointments/{appointment_id}/cancel - Changes status to cancelled and frees up the doctor's availability.
