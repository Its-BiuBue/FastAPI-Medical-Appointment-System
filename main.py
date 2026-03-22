from fastapi import FastAPI, HTTPException, status, Query
from pydantic import BaseModel, Field
from typing import Optional
import math

# Q1: Create main.py, import FastAPI, create app
app = FastAPI()

# ==========================================
# MOCK DATABASE
# ==========================================

# Q2: Create doctors list
doctors = [
    {"id": 1, "name": "Dr. Sharma", "specialization": "Cardiologist", "fee": 1500, "experience_years": 15, "is_available": True},
    {"id": 2, "name": "Dr. Gupta", "specialization": "Dermatologist", "fee": 800, "experience_years": 8, "is_available": True},
    {"id": 3, "name": "Dr. Khan", "specialization": "Pediatrician", "fee": 1000, "experience_years": 12, "is_available": False},
    {"id": 4, "name": "Dr. Singh", "specialization": "General", "fee": 500, "experience_years": 5, "is_available": True},
    {"id": 5, "name": "Dr. Patel", "specialization": "Cardiologist", "fee": 2000, "experience_years": 20, "is_available": True},
    {"id": 6, "name": "Dr. Verma", "specialization": "General", "fee": 600, "experience_years": 7, "is_available": False},
]
doctor_counter = 7

# Q4: Create appointments list and counter
appointments = []
appt_counter = 1


# ==========================================
# PYDANTIC MODELS
# ==========================================

# Q6 & Q9: AppointmentRequest model
class AppointmentRequest(BaseModel):
    patient_name: str = Field(..., min_length=2)
    doctor_id: int = Field(..., gt=0)
    date: str = Field(..., min_length=8)
    reason: str = Field(..., min_length=5)
    appointment_type: str = Field(default="in-person")
    senior_citizen: bool = Field(default=False)

# Q11: NewDoctor model
class NewDoctor(BaseModel):
    name: str = Field(..., min_length=2)
    specialization: str = Field(..., min_length=2)
    fee: int = Field(..., gt=0)
    experience_years: int = Field(..., gt=0)
    is_available: bool = Field(default=True)


# ==========================================
# HELPER FUNCTIONS (Plain Python)
# ==========================================

# Q7: Helper to find doctor
def find_doctor(doctor_id: int):
    for doc in doctors:
        if doc["id"] == doctor_id:
            return doc
    return None

# Q7 & Q9: Helper to calculate fee
def calculate_fee(base_fee: int, appointment_type: str, senior_citizen: bool):
    if appointment_type == "video":
        calculated_fee = base_fee * 0.80
    elif appointment_type == "emergency":
        calculated_fee = base_fee * 1.50
    else:
        calculated_fee = base_fee * 1.00 

    discounted_fee = calculated_fee
    if senior_citizen:
        discounted_fee = calculated_fee * 0.85 
        
    return {"original_fee": calculated_fee, "discounted_fee": discounted_fee}

# Q10: Helper to filter doctors
def filter_doctors_logic(docs_list, specialization, max_fee, min_experience, is_available):
    filtered = docs_list
    if specialization is not None:
        filtered = [d for d in filtered if d["specialization"].lower() == specialization.lower()]
    if max_fee is not None:
        filtered = [d for d in filtered if d["fee"] <= max_fee]
    if min_experience is not None:
        filtered = [d for d in filtered if d["experience_years"] >= min_experience]
    if is_available is not None:
        filtered = [d for d in filtered if d["is_available"] == is_available]
    return filtered


# ==========================================
# ROOT ENDPOINT
# ==========================================

# Q1: Welcome message
@app.get("/")
def read_root():
    return {"message": "Welcome to MediCare Clinic"}


# ==========================================
# DOCTOR ENDPOINTS (Fixed Routes First)
# ==========================================

# Q2: Get all doctors
@app.get("/doctors")
def get_all_doctors():
    available_docs = [doc for doc in doctors if doc["is_available"]]
    return {
        "total": len(doctors),
        "available_count": len(available_docs),
        "doctors": doctors
    }

# Q5: Doctors Summary
@app.get("/doctors/summary")
def get_doctors_summary():
    available_count = sum(1 for d in doctors if d["is_available"])
    most_experienced = max(doctors, key=lambda d: d["experience_years"])
    cheapest = min(doctors, key=lambda d: d["fee"])
    
    spec_counts = {}
    for doc in doctors:
        spec = doc["specialization"]
        spec_counts[spec] = spec_counts.get(spec, 0) + 1

    return {
        "total_doctors": len(doctors),
        "available_count": available_count,
        "most_experienced_doctor": most_experienced["name"],
        "cheapest_consultation_fee": cheapest["fee"],
        "specialization_counts": spec_counts
    }

# Q10: Filter Doctors
@app.get("/doctors/filter")
def filter_doctors(
    specialization: Optional[str] = None, 
    max_fee: Optional[int] = None, 
    min_experience: Optional[int] = None, 
    is_available: Optional[bool] = None
):
    filtered = filter_doctors_logic(doctors, specialization, max_fee, min_experience, is_available)
    return {"total_found": len(filtered), "doctors": filtered}

# Q16: Search Doctors
@app.get("/doctors/search")
def search_doctors(keyword: str = Query(..., min_length=1)):
    keyword_lower = keyword.lower()
    matches = [
        d for d in doctors 
        if keyword_lower in d["name"].lower() or keyword_lower in d["specialization"].lower()
    ]
    if not matches:
        return {"message": f"No doctors found matching '{keyword}'."}
    return {"total_found": len(matches), "results": matches}

# Q17: Sort Doctors
@app.get("/doctors/sort")
def sort_doctors(sort_by: str = "fee", order: str = "asc"):
    valid_sorts = ["fee", "name", "experience_years"]
    if sort_by not in valid_sorts:
        raise HTTPException(status_code=400, detail=f"sort_by must be one of {valid_sorts}")
    if order not in ["asc", "desc"]:
        raise HTTPException(status_code=400, detail="order must be 'asc' or 'desc'")
        
    reverse = (order == "desc")
    sorted_docs = sorted(doctors, key=lambda d: d[sort_by], reverse=reverse)
    return {"sort_by": sort_by, "order": order, "results": sorted_docs}

# Q18: Paginate Doctors
@app.get("/doctors/page")
def paginate_doctors(page: int = Query(1, ge=1), limit: int = Query(3, ge=1, le=10)):
    start = (page - 1) * limit
    end = start + limit
    total_pages = math.ceil(len(doctors) / limit)
    return {
        "total": len(doctors),
        "total_pages": total_pages,
        "page": page,
        "limit": limit,
        "results": doctors[start:end]
    }

# Q20: Browse Doctors (Combine filter -> sort -> paginate)
@app.get("/doctors/browse")
def browse_doctors(
    keyword: Optional[str] = None,
    sort_by: str = "fee",
    order: str = "asc",
    page: int = Query(1, ge=1),
    limit: int = Query(4, ge=1, le=10)
):
    results = doctors
    if keyword:
        k = keyword.lower()
        results = [d for d in results if k in d["name"].lower() or k in d["specialization"].lower()]
        
    valid_sorts = ["fee", "name", "experience_years"]
    if sort_by in valid_sorts and order in ["asc", "desc"]:
        reverse = (order == "desc")
        results = sorted(results, key=lambda d: d[sort_by], reverse=reverse)
        
    total_found = len(results)
    total_pages = math.ceil(total_found / limit)
    start = (page - 1) * limit
    paginated_results = results[start:start + limit]
    
    return {
        "metadata": {
            "keyword": keyword,
            "sort_by": sort_by,
            "order": order,
            "page": page,
            "limit": limit,
            "total_found": total_found,
            "total_pages": total_pages
        },
        "results": paginated_results
    }


# ==========================================
# DOCTOR ENDPOINTS (Variable Routes)
# ==========================================

# Q3: Get doctor by ID
@app.get("/doctors/{doctor_id}")
def get_doctor_by_id(doctor_id: int):
    doc = find_doctor(doctor_id)
    if not doc:
        return {"error": "Doctor not found"}
    return doc

# Q11: Add a new doctor
@app.post("/doctors", status_code=status.HTTP_201_CREATED)
def add_doctor(doc: NewDoctor):
    global doctor_counter
    for existing in doctors:
        if existing["name"].lower() == doc.name.lower():
            raise HTTPException(status_code=400, detail="Doctor with this name already exists")
            
    new_doc = doc.dict()
    new_doc["id"] = doctor_counter
    doctor_counter += 1
    doctors.append(new_doc)
    return new_doc

# Q12: Update doctor details
@app.put("/doctors/{doctor_id}")
def update_doctor(doctor_id: int, fee: Optional[int] = None, is_available: Optional[bool] = None):
    doc = find_doctor(doctor_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Doctor not found")
        
    if fee is not None:
        doc["fee"] = fee
    if is_available is not None:
        doc["is_available"] = is_available
        
    return {"message": "Doctor updated successfully", "doctor": doc}

# Q13: Delete a doctor
@app.delete("/doctors/{doctor_id}")
def delete_doctor(doctor_id: int):
    doc = find_doctor(doctor_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Doctor not found")
        
    has_active = any(
        a["doctor_name"] == doc["name"] and a["status"] == "scheduled" 
        for a in appointments
    )
    if has_active:
        raise HTTPException(status_code=400, detail="Cannot delete doctor with scheduled appointments")
        
    doctors.remove(doc)
    return {"message": f"Doctor {doc['name']} removed successfully."}


# ==========================================
# APPOINTMENT ENDPOINTS (Fixed Routes First)
# ==========================================

# Q4: Get all appointments
@app.get("/appointments")
def get_all_appointments():
    return {
        "total": len(appointments),
        "appointments": appointments
    }

# Q15: Active Appointments
@app.get("/appointments/active")
def get_active_appointments():
    active = [a for a in appointments if a["status"] in ["scheduled", "confirmed"]]
    return {"total": len(active), "results": active}

# Q19: Search Appointments
@app.get("/appointments/search")
def search_appointments(patient_name: str):
    matches = [a for a in appointments if patient_name.lower() in a["patient_name"].lower()]
    return {"total_found": len(matches), "results": matches}

# Q19: Sort Appointments
@app.get("/appointments/sort")
def sort_appointments(sort_by: str = "fee", order: str = "asc"):
    if sort_by not in ["fee", "date"]:
        raise HTTPException(status_code=400, detail="Can only sort by 'fee' or 'date'")
        
    reverse = (order == "desc")
    sort_key = "discounted_fee" if sort_by == "fee" else "date"
    sorted_appts = sorted(appointments, key=lambda a: a[sort_key], reverse=reverse)
    return {"sort_by": sort_by, "order": order, "results": sorted_appts}

# Q19: Paginate Appointments
@app.get("/appointments/page")
def paginate_appointments(page: int = Query(1, ge=1), limit: int = Query(3, ge=1, le=10)):
    start = (page - 1) * limit
    total_pages = math.ceil(len(appointments) / limit)
    return {
        "page": page,
        "limit": limit,
        "total_pages": total_pages,
        "results": appointments[start:start + limit]
    }


# ==========================================
# APPOINTMENT ENDPOINTS (Variable Routes)
# ==========================================

# Q15: Appointments by specific doctor
@app.get("/appointments/by-doctor/{doctor_id}")
def get_appointments_by_doctor(doctor_id: int):
    doc = find_doctor(doctor_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Doctor not found")
        
    matches = [a for a in appointments if a["doctor_name"] == doc["name"]]
    return {"total": len(matches), "results": matches}

# Q8 & Q9: Create Appointment
@app.post("/appointments", status_code=status.HTTP_201_CREATED)
def create_appointment(req: AppointmentRequest):
    global appt_counter
    
    doc = find_doctor(req.doctor_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Doctor not found")
    if not doc["is_available"]:
        raise HTTPException(status_code=400, detail="Doctor is not available")
        
    fee_details = calculate_fee(doc["fee"], req.appointment_type, req.senior_citizen)
    
    # 🎯 FIX FOR Q8/Q14 LOGIC: Mark doctor unavailable upon booking
    doc["is_available"] = False 
    
    new_appt = {
        "appointment_id": appt_counter,
        "patient_name": req.patient_name,
        "doctor_name": doc["name"],
        "date": req.date,
        "appointment_type": req.appointment_type,
        "reason": req.reason,
        "original_fee": fee_details["original_fee"],
        "discounted_fee": fee_details["discounted_fee"],
        "status": "scheduled" 
    }
    
    appointments.append(new_appt)
    appt_counter += 1
    return new_appt

# Q14: Confirm appointment
@app.post("/appointments/{appointment_id}/confirm")
def confirm_appointment(appointment_id: int):
    for a in appointments:
        if a["appointment_id"] == appointment_id:
            a["status"] = "confirmed"
            return {"message": "Appointment confirmed", "appointment": a}
    raise HTTPException(status_code=404, detail="Appointment not found")

# Q14: Cancel appointment
@app.post("/appointments/{appointment_id}/cancel")
def cancel_appointment(appointment_id: int):
    for a in appointments:
        if a["appointment_id"] == appointment_id:
            a["status"] = "cancelled"
            
            # 🎯 FIX FOR Q14 LOGIC: Mark doctor available again upon cancellation
            for d in doctors:
                if d["name"] == a["doctor_name"]:
                    d["is_available"] = True
                    break
                    
            return {"message": "Appointment cancelled and doctor marked available.", "appointment": a}
    raise HTTPException(status_code=404, detail="Appointment not found")

# Q15: Complete appointment
@app.post("/appointments/{appointment_id}/complete")
def complete_appointment(appointment_id: int):
    for a in appointments:
        if a["appointment_id"] == appointment_id:
            a["status"] = "completed"
            return {"message": "Appointment completed", "appointment": a}
    raise HTTPException(status_code=404, detail="Appointment not found")