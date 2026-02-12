# serene
studio 7a

το android studio μας έιναι στο releases.

**Εγκατάσταση & Εκτέλεση (Backend)**
1. pip install fastapi uvicorn sqlalchemy firebase-admin
2. Εκκινήστε τον server μέσα στον φάκελο που είναι τα python αρχεία σας με την εντολή: python main.py

**Εγκατάσταση & Εκτέλεση (Backend)**

H εφαρμογή Android επικοινωνεί με το API μέσω του ApiService. 
Βεβαιωθείτε ότι το Base URL στην εφαρμογή δείχνει την IP του server σας (π.χ. http://192.168.1.XX:5000/)


**Tεχνολογικό Stack**

Backend: FastAPI (Python 3.9+).
Database: SQLite με SQLAlchemy ORM.
Mobile App: Android (Java/Kotlin) με Retrofit για δικτυακή επικοινωνία.
Real-time Processing: Ασύγχρονη επεξεργασία δεδομένων (Asyncio).


**Κύριες Λειτουργίες**

Real-time Stress Ingest: Λήψη και επεξεργασία δεδομένων EDA, HRV (μέσω Beat Intervals), θερμοκρασίας και κίνησης (επιταχυνσιόμετρο).
Smart Stress Algorithm: Υπολογισμός άγχους με αυτόματη αντιστάθμιση κίνησης (Motion Compensation) για μείωση του θορύβου στα δεδομένα.
Event Calendar: Προγραμματισμός δραστηριοτήτων με αυτόματες υπενθυμίσεις
Relaxation Library: Κατάλογος με τεχνικές χαλάρωσης (Box Breathing, Tapping, κ.α.) και καταγραφή ολοκλήρωσης αυτών.
Analytics & History: Οπτικοποίηση δεδομένων ανά ημέρα, εβδομάδα, μήνα ή έτος.
