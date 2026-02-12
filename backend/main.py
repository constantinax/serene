from fastapi import FastAPI, Depends, HTTPException, Body, Form, File, UploadFile
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
import math, os, shutil
import logging
import asyncio
from calendar import monthrange
import database
import models
import schemas
from database import SessionLocal
from tasks import check_event_reminders, refresh_materialized_view 

app = FastAPI()

if not os.path.exists("static"):
    os.makedirs("static")
    os.makedirs("static/profiles")

# 2. Το "μαγικό" mount για τις φωτογραφίες
app.mount("/static", StaticFiles(directory="static"), name="static")

latest_reading = {}
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@app.post("/api/v1/user/upload-profile-image")
async def upload_profile_image(
    username: str = Form(...), 
    profile_image: UploadFile = File(...),
    db: Session = Depends(database.get_db)
):
    file_extension = profile_image.filename.split(".")[-1]
    file_path = f"static/profiles/{username}.{file_extension}"

    # Αποθήκευση του αρχείου στον σκληρό δίσκο
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(profile_image.file, buffer)

    user = db.query(models.User).filter(models.User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user.profile_image = file_path
    db.commit()

    return {"message": "Φωτογραφία αποθηκεύτηκε!", "url": f"/{file_path}"}

# ==========================================
# 1. STARTUP: ΔΗΜΙΟΥΡΓΙΑ ΠΙΝΑΚΩΝ & SEED DATA
# ==========================================
async def run_reminder_task():
    """Αυτή η συνάρτηση τρέχει στο παρασκήνιο για πάντα."""
    while True:
        db = database.SessionLocal()
        try:
            check_event_reminders(db)
        except Exception as e:
            print(f"Reminder Task Error: {e}")
        finally:
            db.close()
        
        await asyncio.sleep(60)

@app.on_event("startup")
async def startup_event():
    models.Base.metadata.create_all(bind=database.engine)
    asyncio.create_task(run_reminder_task())
    asyncio.create_task(refresh_materialized_view())

    db = database.SessionLocal()
    # Ελέγχουμε αν η βάση είναι άδεια για να βάλουμε τα αρχικά δεδομένα
    if db.query(models.Task).count() == 0:
        initial_tasks = [
           # 1. ΑΝΑΠΝΟΗ
            models.Task(
                title="Αναπνοή «4-4-4» (Box Breathing)",
                description="Βαθιά αναπνοή κράτημα και εκπνοή σε ίσους χρόνους",
                duration="2 λεπτά",
                category="home, outdoor",
                is_favorite=False,
                details="""Η αναπνοή 4-4-4, ή αλλιώς Αναπνοή σε Κουτί, είναι μια απλή τεχνική για την ανακούφιση από το στρες. Σταθεροποιεί την ρηχή και γρήγορη αναπνοή που προκαλείται από το άγχος και ενεργοποιεί το παρασυμπαθητικό νευρικό σύστημα για να επαναφέρει το σώμα στο παρόν


Οδηγίες:
1. Εισπνοή από τη μύτη για 4 δευτερόλεπτα.
2. Κράτημα της αναπνοής για 4 δευτερόλεπτα.
3. Εκπνοή από το στόμα για 4 δευτερόλεπτα.
4. Κράτημα (με άδειους πνεύμονες) για 4 δευτερόλεπτα.
"""
            ),


            # 2. ΑΥΤΟΑΓΚΑΛΙΑΣΜΑ
            models.Task(
                title="Αυτοαγκάλιασμα",
                description="Αγκαλιάζεις σφιχτά τον εαυτό σου για αίσθημα ασφάλειας.",
                duration="3 λεπτά",
                category="home",
                is_favorite=False,
                details="""Το αυτοαγκάλιασμα είναι μια τεχνική αυτο-ρύθμισης συναισθημάτων που απελευθερώνει ωκυτοκίνη (προσφέρει αίσθημα προστασίας και ανακούφισης).


Οδηγίες:
1. Σταύρωσε τα χέρια  στο στήθος, ώστε οι παλάμες να ακουμπούν τους ώμους.
2. Κούνα τις παλάμες σου πάνω κάτω στα χέρια σου.
3. Συνόδευσε με αργές αναπνοές.
4. Μείνε σε αυτή τη θέση μέχρι να νιώσεις τους παλμούς σου να ηρεμούν."""
            ),


            # 3. ΘΕΤΙΚΕΣ ΔΗΛΩΣΕΙΣ
            models.Task(
                title="Θετικές Δηλώσεις",
                description="Επανάληψη φράσεων για οαματισμό και θετικές σκέψεις.",
                duration="1 λεπτό",
                category="home, outdoor",
                is_favorite=False,
                details="""Οι θετικές δηλώσεις είναι σύντομες προτάσεις που αντικαθιστούν τις αρνητικές σκέψεις και αναπρογεαμματίζουν τον τρόπου που αντιλαμβανόμαστε τον εαυτό. Πείτε τις δηλώσεις δυνατά και προσπάθησε να νιώσεις την αλήθεια των λέξεων όσο τις προφέρεις.


Μέρη για να πείτε τις δηλώσεις σας:
• Καθρέφτες
• Δίπλα στον υπολογιστή σας
• Στον τοίχο"""
            ),


            # 4. ΙΑΠΩΝΙΚΗ ΤΕΧΝΙΚΗ
            models.Task(
                title="Ιαπωνική Τεχνική (Jin Shin Jyutsu)",
                description="Πίεση συγκεκριμένων δαχτύλων για εξισορρόπηση συναισθημάτων.",
                duration="3 λεπτά",
                category="home, outdoor",
                is_favorite=False,
                details="""Το Jin Shin Jyutsu είναι μια τεχνική που βασίζεται στην ιδέα ότι κάθε δάχτυλο συνδέεται με ένα συναίσθημα. Πιάστε το δάχτυλο που αντιστοιχεί στο συναίσθημα που θέλετε να εξισορροπήσετε με την παλάμη και τα δάχτυλα του άλλου χεριού (σαν να το αγκαλιάζετε ελαφρά). Λειτουργεί όταν νιώσετε έναν σταθερό, ρυθμικό παλμό στο δάχτυλο. Αν ο παλμός είναι πολύ έντονος ή ακανόνιστος, μείνετε εκεί μέχρι να ηρεμήσει. Μπορείτε να κάνετε ένα συγκεκριμένο δάχτυλο ή και τα δέκα διαδοχικά..


Τα Δάχτυλα και τα Συναισθήματα:
• Αντίχειρας: Σταματά την ανησυχία και την υπερβολική σκέψη, προσφέροντας άμεση ηρεμία στον νου.
• Δείκτης: Διώχνει τον φόβο και τον πανικό, βοηθώντας το σώμα να χαλαρώσει από τη νοητική πίεση.
• Μέσος: Μαλακώνει τον εκνευρισμό και την εσωτερική ένταση, επαναφέροντας τη συναισθηματική ισορροπία.
• Παράμεσος: Απελευθερώνει τη θλίψη και το σφίξιμο, επιτρέποντας στο σώμα να αναπνεύσει ελεύθερα.
• Μικρό Δάχτυλο: Σταματά την υπερπροσπάθεια και το στρες των κοινωνικών προσδοκιών, χαλαρώνοντας την καρδιά.
"""
            ),


            # 5. ΔΙΑΛΟΓΙΣΜΟΣ
            models.Task(
                title="Καθοδηγούμενος Διαλογισμός",
                description="Χαλάρωσε ακούγοντας φωνητικές οδηγίες.",
                duration="5 λεπτά",
                category="home",
                is_favorite=False,
                details="""Ένας αφηγητής σε καθοδηγεί μέσω ασκήσεων αναπνοής και οραματισμού. Αν το να κάθεσαι ήσυχα με τις σκέψεις σου σου φαίνεται τρομακτικό, ο καθοδηγούμενος διαλογισμός μπορεί να είναι ένα εξαιρετικό σημείο για να ξεκινήσεις. Βοηθά στη συγκέντρωση και την διαχείριση των διάσπαρτων αγχωτικών σκέψεων.
"""
            ),


            # 6. ΜΟΥΣΙΚΗ
            models.Task(
                title="Χαλαρωτική Μουσική",
                description="Εστίασε στις εναλλαγές του ήχου και του ρυθμού.",
                duration="10 λεπτά",
                category="home, outdoor",
                is_favorite=False,
                details="""Η μουσική με αργό τέμπο (περίπου 60 χτύπους το λεπτό) μπορεί να συγχρονίσει τους καρδιακούς παλμούς με τον ρυθμό της, προκαλώντας φυσική επιβράδυνση της αναπνοής και ρύθμιση του νευρικού συστήματος.


Οδηγίες:
• Χρησιμοποίησε ακουστικά για καλύτερη απομόνωση.
• Κλείσε τα μάτια και συγκεντρώσου στους ήχους.  
• Άφησε τη μελωδία να σε παρασύρει, διώχνοντας τις παρεμβατικές σκέψεις."""
            ),


            # 7. PMR (Προοδευτική Μυϊκή Χαλάρωση)
            models.Task(
                title="Προοδευτική Μυϊκή Χαλάρωση (PMR)",
                description="Σύσπαση και χαλάρωση των μυών.",
                duration="3 λεπτά",
                category="home, outdoor",
                is_favorite=False,
                details="""Η προοδευτική μυϊκή χαλάρωση σου μαθαίνει να αναγνωρίζεις τη διαφορά μεταξύ έντασης και χαλάρωσης. Τεντώνοντας και χαλαρώνοντας διαφορετικές μυϊκές ομάδες με μια συγκεκριμένη σειρά, προκαλείς μια αίσθηση ανακούφισης που σε ηρεμεί. 


Συμβουλές:
• Δώστε ιδιαίτερη προσοχή στο να μην κρατάτε την αναπνοή ενώ τεντώνετε τους μύες.
• Εισπνεύστε ενώ δημιουργείτε ένταση και εκπνεύστε όταν απελευθερώνετε την ένταση
• Συνιστάται η δημιουργία έντασης και χαλάρωσης αρκετές φορές στις ίδιες μυϊκές ομάδες, με μειωμένους βαθμούς έντασης.


Προσοχή:
• Μην καταπονείτε και μην τεντώνετε υπερβολικά τον μυ.
• Εάν κάποια από τις ασκήσεις προκαλεί δυσφορία ή κράμπες, χαλαρώστε, σταματήστε ή παραλείψτε εντελώς αυτό το μέρος του σώματος.
"""
            ),


            # 8. TAPPING (EFT)
            models.Task(
                title="EFT - Tapping",
                description="Ελαφρά χτυπήματα σε ενεργειακά σημεία.",
                duration="2 λεπτά",
                category="home",
                is_favorite=False,
                details="""Το EFT (Emotional Freedom Technique) ή «Tapping» είναι μία τεχνική που χρησιμοποιώντας τις ακρες των δαχτύλων σου χτυπάς ελαφρά συγκεκριμένα σημεία του σώματος (βελονιστικά σημεία). Φαντάσου το σαν έναν τρόπο να «ξεμπλοκάρεις» το κέντρο του εγκεφάλου σου που ελέγχει το άγχος και τον φόβο .


Οδηγίες:
Χρησιμοποίησε δύο δάχτυλα (δείκτη και μέσο) για να κάνεις ελαφρά, ρυθμικά χτυπήματα (tapping) περίπου 5-7 φορές σε κάθε σημείο, ενώ επικεντρώνεσαι στη σκέψη που σε αγχώνει.


Τα Σημεία:
• Κορυφή του κεφαλιού: Βοηθά στην πνευματική διαύγεια.
• Φρύδι: Απελευθέρωση φόβου και ανυπομονησίας.
• Πλάι του ματιού: Ανακούφιση από θυμό και ένταση.
• Κλείδα: Πολύ σημαντικό σημείο για το γενικό άγχος και την ασφάλεια.
• Πλάι της παλάμης (Karate Chop): Απελευθέρωση εσωτερικής αντίστασης.
• Πηγούνι: Απελευθέρωση από ενοχές ή σύγχυση.
• Κάτω από τη μασχάλη: Απελευθέρωση ανασφάλειας."""
            )
        ]
        db.add_all(initial_tasks)
        db.commit()
        print("--- DATABASE SEEDED WITH TASKS & DETAILS ---")
    db.close()

# ==========================================
# 2. DEVICE REGISTRATION
# ==========================================
@app.post("/api/v1/devices/register")
def registered_device(
    token_data: schemas.DeviceTokenCreate,
    db: Session = Depends(database.get_db)
):
    device = db.query(models.UserDevice)\
        .filter_by(fcm_token=token_data.token)\
        .first()

    if not device:
        db.add(models.UserDevice(
            user_id=token_data.user_id,
            fcm_token=token_data.token,
            device_name=token_data.device_name
        ))
        db.commit()

    return {"status": "registered"}

@app.get("/api/v1/calendar/{user_id}")
def get_calendar_data(
    user_id: str, 
    year: int = None, 
    month: int = None, 
    db: Session = Depends(database.get_db)
):
    now = datetime.now()
    if year is None: year = now.year
    if month is None: month = now.month

    # Βρίσκουμε πόσες μέρες έχει ο μήνας
    _, num_days = monthrange(year, month)
    calendar_data = []

    for day in range(1, num_days + 1):
        date_str = f"{year}-{month:02d}-{day:02d}"
        
        # A. ΒΡΕΣ ΤΑ ΠΡΟΓΡΑΜΜΑΤΙΣΜΕΝΑ (Events)
        scheduled_events = db.query(models.Event).filter(
        models.Event.user_id == user_id,
        models.Event.start_date == date_str 
        ).all()
        
        total_tasks = len(scheduled_events)

        # B. ΒΡΕΣ ΤΑ ΟΛΟΚΛΗΡΩΜΕΝΑ (History)
        completed_tasks_count = db.query(models.UserActivity).filter(
            models.UserActivity.user_id == user_id,
            func.date(models.UserActivity.completed_at) == date_str
        ).count()

        # Γ. STATUS
        progress = 0
        if total_tasks > 0:
            progress = (completed_tasks_count / total_tasks) * 100
            if progress > 100: progress = 100
        elif completed_tasks_count > 0:
            progress = 100 

        status = "none"
        current_date_obj = datetime(year, month, day)
        today_obj = datetime(now.year, now.month, now.day)

        if progress == 100: status = "completed"
        elif progress > 0: status = "partial"
        elif total_tasks > 0 and current_date_obj < today_obj: status = "missed"
        elif total_tasks > 0: status = "pending"

        event_details = []
        for ev in scheduled_events:
            event_details.append({
                "id": ev.id,
                "title": ev.title,
                "description": ev.notes or "",
                "time": ev.start_time or "",
                "is_done": False 
            })

        calendar_data.append({
            "day": day,
            "full_date": date_str,
            "progress": int(progress),
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks_count,
            "status": status,
            "events": event_details
        })

    return calendar_data

# ==========================================
# 3. ACTIVITIES / EVENTS
# ==========================================

# --- ΠΡΟΣΘΗΚΗ ACTIVITY ---
@app.post("/api/v1/events")
async def add_activity(data: dict = Body(...), db: Session = Depends(database.get_db)):
    ev = models.Event(
        user_id=str(data.get("user_id")),
        title=data.get("title"),
        location=data.get("location"),
        event_type=data.get("type"), # Το αλλάξαμε σε event_type στο model
        start_date=data.get("start_date") or data.get("startDate"),
        start_time=data.get("start_time") or data.get("startTime"),
        end_date=data.get("end_date") or data.get("endDate"),
        end_time=data.get("end_time") or data.get("endTime"),
        notes=data.get("notes")
    )
    db.add(ev)
    db.commit()
    return {"status": "success", "id": ev.id}

# --- ΛΗΨΗ ACTIVITIES ---
@app.get("/api/v1/activities/{user_id}") 
async def get_events(user_id: str, db: Session = Depends(database.get_db)):
    # Χρησιμοποιούμε το models.Event
    events = db.query(models.Event)\
        .filter(models.Event.user_id == user_id)\
        .order_by(models.Event.start_date.asc())\
        .all()

    return [{
        "id": ev.id,
        "title": ev.title,
        "location": ev.location,
        "type": ev.event_type,      
        "startDate": ev.start_date,
        "startTime": ev.start_time,
        "endDate": ev.end_date,
        "endTime": ev.end_time,
        "notes": ev.notes
    } for ev in events]

# --- UPDATE EVENT ---
@app.put("/api/v1/events/{event_id}")
async def update_event(event_id: int, data: dict, db: Session = Depends(database.get_db)):
    event = db.query(models.Event).filter(models.Event.id == event_id).first()
    
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    try:
        # Ενημέρωση βασικών πεδίων
        event.title = data.get("title", event.title)
        event.location = data.get("location", event.location)
        event.notes = data.get("notes", event.notes)

     
        event.event_type = data.get("type", event.event_type)

        # Ενημέρωση ημερομηνιών και ωρών 
        event.start_date = data.get("startDate", event.start_date)
        event.start_time = data.get("startTime", event.start_time)
        event.end_date = data.get("endDate", event.end_date)
        event.end_time = data.get("endTime", event.end_time)

        # Ενημέρωση ειδοποίησης (αν υπάρχει)
        if "notification" in data:
            event.notify_before = data.get("notification")

        db.commit()
        return {"status": "success", "message": "Updated successfully"}
    
    except Exception as e:
        db.rollback()
        print(f"Update Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# --- DELETE EVENT ---
@app.delete("/api/v1/events/{event_id}")
async def delete_event(event_id: int, db: Session = Depends(database.get_db)):
    event = db.query(models.Event).get(event_id)
    if not event:
        raise HTTPException(404, "Event not found")

    db.delete(event)
    db.commit()
    return {"status": "deleted"}

# ==========================================
# 4. BIOMETRICS & HISTORY
# ==========================================
@app.post("/api/v1/data/ingest")
async def ingest_biometrics(data: schemas.BiometricDataCreate, db: Session = Depends(database.get_db)):
    try:
        # Λήψη δεδομένων
        user_id = data.user_id
        # Χρήση default τιμών (0.0) αν έρθει κάτι λάθος, αν και το Pydantic το κόβει νωρίτερα
        eda = data.eda if data.eda is not None else 0.0
        temp = data.temp if data.temp is not None else 0.0
        hr = data.hr if data.hr is not None else 0.0
        bi = data.bi if data.bi is not None else 0.0

        # 1. Baseline & History: 
        history = db.query(models.RawBiometrics).filter(
            models.RawBiometrics.user_id == data.user_id
        ).order_by(models.RawBiometrics.time.desc()).limit(60).all()

        # 2. HRV Score (RMSSD)
        rmssd_score = 0
        if len(history) > 0: 
            diff = abs(bi - history[0].hrv_bi)
            rmssd_score = max(0, 100 - (diff * 1000)) 

        # 3. EDA Score (Η ΜΕΓΑΛΗ ΑΛΛΑΓΗ)
        if history:
            eda_baseline = min(h.eda_value for h in history)
        else:
            eda_baseline = eda

        eda_diff = max(0, eda - eda_baseline)
        
        # Προσαρμογή ευαισθησίας
        eda_score = min((eda_diff / (eda_baseline + 0.1)) * 500, 100)

        # 4. Temperature Validation
        temp_trend = 0
        # Συγκρίνουμε με τον μέσο όρο των παλιών για να αποφύγουμε θόρυβο
        if history:
            avg_old_temp = sum(h.temperature for h in history) / len(history)
            if temp < avg_old_temp - 0.1: # Αν έπεσε πάνω από 0.1 βαθμό
                temp_trend = 100

        # 5. Artifact Removal (Κίνηση)
        mag = math.sqrt(data.accel_x**2 + data.accel_y**2 + data.accel_z**2)
        movement = abs(mag - 1.0)
        move_score = min(movement / 0.5, 1.0)

        # 6. FUSION
        base_stress = (eda_score * 0.5) + (rmssd_score * 0.3) + (temp_trend * 0.2)
        
        # Damping λόγω κίνησης
        confidence = 1.0 if movement < 0.2 else 0.4
        final_anxiety = base_stress * confidence

        final_anxiety = round(max(5.0, min(final_anxiety, 100.0)), 2)
        now = datetime.now()

        # Αποθήκευση
        db.add(models.RawBiometrics(user_id=user_id, eda_value=eda, temperature=temp,
                                    heart_rate=hr, hrv_bi=bi, movement_val=movement, is_moving=move_score, time=now))
        db.add(models.AnxietyLevel(user_id=user_id, anxiety_score=final_anxiety, time=now))
        db.commit()

        # Ενημέρωση Live Dictionary
        latest_reading[user_id] = {
            "eda": eda,
            "temp": temp,
            "hr": hr,
            "hrv_bi": bi,
            "stress_level": final_anxiety,
            "is_moving": move_score,
            "movement_val": movement,
            "timestamp": now.isoformat()
        }

        return {"status": "success", "stress_level": final_anxiety}

    except Exception as e:
        db.rollback()
        # Επιστροφή default αντί για crash αν κάτι πάει στραβά
        print(f"Error processing biometrics: {e}")
        return {"status": "error", "stress_level": 5.0}
     
# ==========================================
# 5. STATS (ΔΙΟΡΘΩΜΕΝΗ ΛΟΓΙΚΗ - ΧΩΡΙΣ /api/v1)
# ==========================================
@app.get("/stats/{period}/{user_id}")
def get_period_stats(period: str, user_id: str, date: str = None, db: Session = Depends(database.get_db)):
    # 1. Διαχείριση Ημερομηνίας Αναφοράς
    if date:
        try:
            ref_date = datetime.strptime(date, "%Y-%m-%d")
        except:
            ref_date = datetime.now()
    else:
        ref_date = datetime.now()

    # Κανονικοποίηση: Ορίζουμε την ώρα στο 00:00:00
    ref_date = ref_date.replace(hour=0, minute=0, second=0, microsecond=0)

    # 2. Καθορισμός ΤΕΛΟΥΣ (End Limit) -> Η αρχή της ΕΠΟΜΕΝΗΣ μέρας
    end_limit = ref_date + timedelta(days=1)
    end_limit_str = end_limit.strftime("%Y-%m-%d")

    # 3. Καθορισμός ΑΡΧΗΣ (Start Limit) ανάλογα με την περίοδο
    if period == "daily":
        start_limit = ref_date  
    elif period == "weekly":
        start_limit = ref_date - timedelta(days=6)  
    elif period == "monthly":
        start_limit = ref_date - timedelta(days=29)  
    else:
        start_limit = ref_date - timedelta(days=364)

    start_limit_str = start_limit.strftime("%Y-%m-%d")

    # 4. QUERIES (Προστέθηκε ο έλεγχος < end_limit για να μην παίρνει τα μελλοντικά)

    # A. EVENTS (Ημερολόγιο)
    calendar_events_count = db.query(models.Event).filter(
        models.Event.user_id == user_id, 
        models.Event.start_date >= start_limit_str,
        models.Event.start_date < end_limit_str  
    ).count()
    
    # B. ACTIVITIES (Τεχνικές)
    techniques_count = db.query(models.UserActivity).filter(
        models.UserActivity.user_id == user_id, 
        models.UserActivity.completed_at >= start_limit,
        models.UserActivity.completed_at < end_limit
    ).count()
    
    # C. ANXIETY (Πίνακας AnxietyLevel)
    anxiety_count = db.query(models.AnxietyLevel).filter(
        models.AnxietyLevel.user_id == user_id, 
        models.AnxietyLevel.time >= start_limit, 
        models.AnxietyLevel.time < end_limit,     
        models.AnxietyLevel.anxiety_score > 50
    ).count()

    return {
        "techniques": techniques_count,
        "activities": calendar_events_count,
        "anxiety": anxiety_count
    }

# Endpoint για να καταγράφει το Android μια ολοκληρωμένη άσκηση
@app.post("/api/v1/tasks/complete")
async def complete_activity(data: schemas.UserActivityCreate, db: Session = Depends(database.get_db)):
    new_activity = models.UserActivity(
        user_id=data.user_id,
        activity_type=data.activity_type, 
        title=data.title,                 
        duration_seconds=data.duration_seconds,
        completed_at=datetime.now()
    )
    db.add(new_activity)
    db.commit()
    return {"status": "success", "id": new_activity.id}

# ==========================================
# 5.5 HISTORY (ΓΡΑΦΗΜΑ & MARKERS)
# ==========================================

@app.get("/api/v1/history/{user_id}", response_model=schemas.HistoryResponse)
async def get_anxiety_history(
    user_id: str, 
    period: str, 
    date: str = None, 
    db: Session = Depends(database.get_db)
):
    # 1. Καθορισμός ημερομηνίας αναφοράς
    ref_date = datetime.now()
    if date:
        try:
            ref_date = datetime.fromisoformat(date)
        except:
            pass 

    data_points = []
    total_sum = 0
    count = 0
    
    # Αρχικοποίηση ορίων (default)
    start_limit = ref_date
    end_limit = ref_date

    # ==========================================
    # 1. DAILY: Όλο το 24ωρο (00:00 - 23:59)
    # ==========================================
    if period == "daily":
        start_of_day = ref_date.replace(hour=0, minute=0, second=0, microsecond=0)
        
        start_limit = start_of_day
        end_limit = start_of_day + timedelta(days=1)

        for i in range(24):
            bucket_start = start_of_day + timedelta(hours=i)
            bucket_end = bucket_start + timedelta(hours=1)

            avg = db.query(func.avg(models.AnxietyLevel.anxiety_score)).filter(
                models.AnxietyLevel.user_id == user_id,
                models.AnxietyLevel.time >= bucket_start,
                models.AnxietyLevel.time < bucket_end
            ).scalar() or 0.0

            data_points.append(schemas.StressDataPoint(
                label=f"{i:02d}",
                avg_anx=round(avg, 1)
            ))

            if avg > 0:
                total_sum += avg
                count += 1

    # ==========================================
    # 2. WEEKLY: Δευτέρα έως Κυριακή
    # ==========================================
    elif period == "weekly":
        days_to_subtract = ref_date.weekday() 
        start_of_week = ref_date - timedelta(days=days_to_subtract)
        start_of_week = start_of_week.replace(hour=0, minute=0, second=0, microsecond=0)
        
        start_limit = start_of_week
        end_limit = start_of_week + timedelta(days=7)

        for i in range(7):
            day_start = start_limit + timedelta(days=i)
            day_end = day_start + timedelta(days=1)

            avg = db.query(func.avg(models.AnxietyLevel.anxiety_score)).filter(
                models.AnxietyLevel.user_id == user_id,
                models.AnxietyLevel.time >= day_start,
                models.AnxietyLevel.time < day_end
            ).scalar() or 0.0

            label_str = day_start.strftime("%a") 
            data_points.append(schemas.StressDataPoint(
                label=label_str,
                avg_anx=round(avg, 1)
            ))

            if avg > 0:
                total_sum += avg
                count += 1

    # ==========================================
    # 3. MONTHLY: Ολόκληρος ο μήνας
    # ==========================================
    elif period == "monthly":
        start_of_month = ref_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        _, num_days = monthrange(start_of_month.year, start_of_month.month)
        end_of_month = start_of_month + timedelta(days=num_days)

        start_limit = start_of_month
        end_limit = end_of_month

        current_start = start_of_month
        week_counter = 1

        while current_start < end_of_month:
            days_until_sunday = 6 - current_start.weekday()
            current_end = current_start + timedelta(days=days_until_sunday + 1)
            if current_end > end_of_month:
                current_end = end_of_month

            avg = db.query(func.avg(models.AnxietyLevel.anxiety_score)).filter(
                models.AnxietyLevel.user_id == user_id,
                models.AnxietyLevel.time >= current_start,
                models.AnxietyLevel.time < current_end
            ).scalar() or 0.0

            data_points.append(schemas.StressDataPoint(
                label=f"W{week_counter}",
                avg_anx=round(avg, 1)
            ))

            if avg > 0:
                total_sum += avg
                count += 1
            
            current_start = current_end
            week_counter += 1

    # ==========================================
    # 4. YEARLY: Ολόκληρο το έτος
    # ==========================================
    else: 
        start_of_year = ref_date.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        
        start_limit = start_of_year
        end_limit = start_of_year.replace(year=start_of_year.year + 1)

        def get_month_range(year, month):
            start = datetime(year, month, 1)
            if month == 12:
                end = datetime(year + 1, 1, 1)
            else:
                end = datetime(year, month + 1, 1)
            return start, end

        for i in range(12):
            curr_month = i + 1
            m_start, m_end = get_month_range(start_of_year.year, curr_month)

            avg = db.query(func.avg(models.AnxietyLevel.anxiety_score)).filter(
                models.AnxietyLevel.user_id == user_id,
                models.AnxietyLevel.time >= m_start,
                models.AnxietyLevel.time < m_end
            ).scalar() or 0.0

            # Επιστροφή στο κλασικό Jan/Feb
            data_points.append(schemas.StressDataPoint(
                label=m_start.strftime("%b"),
                avg_anx=round(avg, 1)
            ))

            if avg > 0:
                total_sum += avg
                count += 1

    # ==========================================
    # ΤΕΛΙΚΑ QUERY
    # ==========================================
    
    overall_avg = (total_sum / count) if count > 0 else 0.0

    completed_tasks = db.query(models.UserActivity).filter(
        models.UserActivity.user_id == user_id,
        models.UserActivity.completed_at >= start_limit,
        models.UserActivity.completed_at < end_limit
    ).order_by(models.UserActivity.completed_at.desc()).all()

    start_str = start_limit.strftime("%Y-%m-%d")
    end_str = end_limit.strftime("%Y-%m-%d")

    events_query = db.query(models.Event).filter(models.Event.user_id == user_id)

    if period == "daily":
        events_query = events_query.filter(models.Event.start_date == start_str)
    else:
        events_query = events_query.filter(
            models.Event.start_date >= start_str,
            models.Event.start_date < end_str
        )

    calendar_activities = events_query.all()

    return {
        "period": period, 
        "overall_average": round(overall_avg, 1), 
        "stress_data": data_points,
        "completed_tasks": completed_tasks,
        "activities": calendar_activities
    }
# ==========================================
# 6. TASKS (ΒΙΒΛΙΟΘΗΚΗ ΑΣΚΗΣΕΩΝ)
# ==========================================
@app.get("/tasks")
def get_tasks(db: Session = Depends(database.get_db)):
    return db.query(models.Task).all()

@app.post("/tasks/{task_id}/toggle-favorite")
def toggle_favorite(task_id: int, db: Session = Depends(database.get_db)):
    task = db.query(models.Task).get(task_id)
    if not task:
        raise HTTPException(404, "Task not found")

    task.is_favorite = not task.is_favorite
    db.commit()
    return {"status": "success", "is_favorite": task.is_favorite}

# ==========================================
# 7. AUTH (LOGIN / SIGNUP)
# ==========================================
@app.post("/login")
async def login(request: dict, db: Session = Depends(database.get_db)):
    return {"status": "success", "message": "Login successful"}

@app.post("/signup")
async def signup(user: dict, db: Session = Depends(database.get_db)):
    return {"status": "success"}


@app.put("/users/{username}")
def update_user(username: str, user_update: schemas.UserUpdate, db: Session = Depends(database.get_db)):
    # 1. Βρες τον χρήστη
    user = db.query(models.User).filter(models.User.username == username).first()
    
    if not user:
        user = models.User(username=username, email="", password="")
        db.add(user)
        db.commit()
        db.refresh(user)

    # 2. Ενημέρωσε τα στοιχεία
    if user_update.username:
        user.username = user_update.username
    if user_update.email:
        user.email = user_update.email
    if user_update.password:
        user.password = user_update.password

    db.commit()
    return {"status": "updated", "username": user.username}


# --- GET: Λήψη όλων των τοποθεσιών του χρήστη ---
@app.get("/api/v1/locations/{username}", response_model=list[schemas.UserLocationResponse])
def get_locations(username: str, db: Session = Depends(database.get_db)):
    return db.query(models.UserLocation).filter(models.UserLocation.user_id == username).all()

# --- POST: Αποθήκευση νέας τοποθεσίας ---
@app.post("/api/v1/locations")
def add_location(location: schemas.UserLocationCreate, db: Session = Depends(database.get_db)):
    db_location = models.UserLocation(**location.dict())
    db.add(db_location)
    db.commit()
    db.refresh(db_location)
    return {"status": "success", "id": db_location.id}

# --- DELETE: Διαγραφή τοποθεσίας ---
@app.delete("/api/v1/locations/{location_id}")
def delete_location(location_id: int, db: Session = Depends(database.get_db)):
    db_loc = db.query(models.UserLocation).filter(models.UserLocation.id == location_id).first()
    if not db_loc:
        raise HTTPException(status_code=404, detail="Location not found")
    db.delete(db_loc)
    db.commit()
    return {"status": "deleted"}

# ==========================================
# 8. RUN SERVER
# ==========================================
if __name__ == "__main__":
    import uvicorn
    # host="0.0.0.0" για πρόσβαση από το δίκτυο/emulator
    uvicorn.run(app, host="0.0.0.0", port=5000)
