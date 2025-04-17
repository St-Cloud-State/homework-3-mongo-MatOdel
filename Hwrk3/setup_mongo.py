from pymongo import MongoClient
from datetime import datetime
from bson.objectid import ObjectId

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["acme_financial"]

# Applications collection
applications = db["applications"]

# ----------- 1. Accept application -----------
def accept_application(name, zipcode):
    application = {
        "name": name,
        "zipcode": zipcode,
        "status": "received",
        "notes": [],
        "created_at": datetime.utcnow()
    }
    result = applications.insert_one(application)
    return str(result.inserted_id)

# ----------- 2. Check status -----------
def check_status(application_id):
    app = applications.find_one({"_id": ObjectId(application_id)})
    if not app:
        return "not found"
    return app["status"]

# ----------- 3. Change status -----------
def change_status(application_id, new_status):
    result = applications.update_one(
        {"_id": ObjectId(application_id)},
        {"$set": {"status": new_status}}
    )
    return result.modified_count > 0

# ----------- 4. Add note to application -----------
def add_note(application_id, message, subphase=None, task=None):
    note = {
        "timestamp": datetime.utcnow(),
        "message": message,
        "subphase": subphase,
        "task": task
    }
    applications.update_one(
        {"_id": ObjectId(application_id)},
        {"$push": {"notes": note}}
    )

# ----------- 5. Get all notes for application -----------
def get_notes(application_id):
    app = applications.find_one({"_id": ObjectId(application_id)})
    if not app:
        return "not found"
    return app.get("notes", [])

# ---------------- Example Test ----------------
if __name__ == "__main__":
    app_id = accept_application("John Doe", "12345")
    print(f"Application ID: {app_id}")

    print("Initial Status:", check_status(app_id))

    change_status(app_id, "processing")
    print("Status after update:", check_status(app_id))

    add_note(app_id, "Started personal details checking", subphase="personal_details", task="verify_name")
    add_note(app_id, "Credit check complete", subphase="credit_check", task="credit_report")
    add_note(app_id, "Loan approved", subphase="certification_check", task="final_review")

    print("Notes:")
    for note in get_notes(app_id):
        print(note)
