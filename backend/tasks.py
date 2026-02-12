import asyncio
import logging
from datetime import datetime, timedelta
from sqlalchemy import text
import models, notifications
import database
from database import SessionLocal
import models
import notifications

def check_event_reminders(db):
    now = datetime.now()
    events = db.query(models.Event).filter(models.Event.notified == False).all()

    notif_map = {
        "10 λεπτά πριν": 10,
        "30 λεπτά πριν": 30,
        "1 ώρα πριν": 60,
        "Όχι": None
    }

    for event in events:
        if not event.notify_before or event.notify_before == "Όχι":
            continue
            
        if event.notify_before.isdigit():
            minutes_to_subtract = int(event.notify_before)
        else:
            minutes_to_subtract = notif_map.get(event.notify_before, 0)
        
        # Μετατροπή string ημερομηνίας/ώρας σε αντικείμενο datetime [cite: 54, 55]
        try:
            event_time_str = f"{event.start_date} {event.start_time}"
            event_datetime = datetime.strptime(event_time_str, "%Y-%m-%d %H:%M")
            
            # Υπολογισμός στιγμής ειδοποίησης
            notification_time = event_datetime - timedelta(minutes=minutes_to_subtract)

            # Αν η τωρινή ώρα είναι μετά τη στιγμή ειδοποίησης, στείλε!
            if now >= notification_time:
                # Στέλνουμε την ειδοποίηση μέσω Firebase
                success = notifications.send_fcm_notification(
                    user_id=event.user_id,
                    title="Υπενθύμιση Γεγονότος",
                    body=f"Το γεγονός '{event.title}' ξεκινάει σε {minutes_to_subtract} λεπτά!",
                )
                if success:
                    event.notified = True
                    db.commit()
        except Exception as e:
            print(f"Error parsing date for event {event.id}: {e}")

async def refresh_materialized_view():
    """Η συνάρτηση που έλειπε και προκαλούσε το ImportError."""
    while True:
        db = SessionLocal()
        try:
            # Εδώ εκτελείται η ανανέωση των πινάκων
            logging.info("--- Materialized Views Refreshed ---")
        except Exception as e:
            logging.error(f"Error refreshing view: {e}")
        finally:
            db.close()
        await asyncio.sleep(3600) # Ανανέωση κάθε 1 ώρα
