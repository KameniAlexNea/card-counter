import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore


class FirebaseConnector:
    def __init__(self):
        cred = credentials.Certificate("data/connection_key.json")
        firebase_admin.initialize_app(cred)
        self.db = firestore.client()

    def add(self, ocr: str, key: str):
        return self.db.collection("id-card").add({"card-id": key, "ocr": ocr})
