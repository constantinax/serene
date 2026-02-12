import os
import logging
from typing import List, Optional
import firebase_admin
from firebase_admin import credentials, messaging
from sqlalchemy.orm import Session
import models 

def init_firebase():
    if firebase_admin._apps:
        return

    try:
        cred = credentials.Certificate("firebase_key.json")
        firebase_admin.initialize_app(cred)
    except Exception as e:
        logging.error(f"Failed to initialize Firebase: {e}")
        raise RuntimeError("Πρέπει να έχεις το αρχείο firebase_key.json στον φάκελο του server!")

def send_fcm_notification(user_id: str, title: str, body: str) -> bool:
    init_firebase()
    
    from database import SessionLocal
    db = SessionLocal()
    
    try:
        devices = db.query(models.UserDevice).filter(
            models.UserDevice.user_id == user_id,
            models.UserDevice.is_active == True
        ).all()

        if not devices:
            logging.warning(f"No active devices for user {user_id}")
            return False

        tokens = [d.fcm_token for d in devices if d.fcm_token]
        
        message = messaging.MulticastMessage(
            notification=messaging.Notification(title=title, body=body),
            tokens=tokens,
        )

        response = messaging.send_multicast(message)
        logging.info(f"Sent {response.success_count} notifications for user {user_id}")
        return response.success_count > 0
    except Exception as e:
        logging.error(f"Error in send_fcm_notification: {e}")
        return False
    finally:
        db.close()

def send_anxiety_alert(user_id: str, title: str, body: str, db: Session) -> int:
    init_firebase()

    devices: List[models.UserDevice] = (
        db.query(models.UserDevice).filter(models.UserDevice.user_id == user_id).all()
    )

    if not devices:
        logging.debug("No devices found for user %s", user_id)
        return 0

    tokens = [device.fcm_token for device in devices if device.fcm_token]
    if not tokens:
        return 0

    message = messaging.MulticastMessage(
        notification=messaging.Notification(title=title, body=body),
        data={"screen": "relaxation_exercises"},
        tokens=tokens,
    )

    try:
        response = messaging.send_multicast(message)
        return response.success_count
    except Exception as exc:
        logging.exception("FCM send failed for user %s", user_id)
        return 0
