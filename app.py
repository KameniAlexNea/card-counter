import io

import easyocr
import firebase_admin
import gradio as gr
from firebase_admin import credentials, firestore
from loguru import logger
from PIL import Image


class EasyOCRReader:
    def __init__(self):
        self.reader = easyocr.Reader(["fr", "en"], gpu=False)

    def chat(self, image: Image.Image):
        # Convert image to bytes
        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format="PNG")
        img_byte_arr = img_byte_arr.getvalue()

        # Call readtext with image bytes
        texts = self.reader.readtext(img_byte_arr, detail=0)
        logger.info(" ".join(texts))
        return " ".join(texts)


class FirebaseConnector:
    def __init__(self):
        cred = credentials.Certificate("data/connection_key.json")
        firebase_admin.initialize_app(cred)
        self.db = firestore.client()

    def add(self, ocr: str, key: str):
        return self.db.collection("id-card").add({"card-id": key, "ocr": ocr})


class VoterCardVerifier:
    def __init__(self):
        self.db = FirebaseConnector()
        self.ocr_engine = EasyOCRReader()

    def verify_card(self, image, card_number):
        # Convertir l'image pour Groq
        if isinstance(image, str):
            image = Image.open(image)

        # Préparer la requête pour le modèle et l'appeler
        ocr_data = self.ocr_engine.chat(image).strip().lower()

        # valider les entrées
        is_valid = ("camer" in ocr_data) and (card_number in ocr_data)

        if is_valid:
            # Sauvegarder dans Firebase
            return self.save_card_number(ocr_data, card_number)
        else:
            return "Numéro de carte non trouvé sur l'image"

    def save_card_number(self, ocr_data, card_number):
        return self.db.add(ocr_data, card_number)


# Interface Gradio
def create_interface():
    verifier = VoterCardVerifier()

    def process(image, card_number):
        if not card_number.strip():
            return "Veuillez entrer un numéro de carte"
        return verifier.verify_card(image, card_number)

    interface = gr.Interface(
        fn=process,
        inputs=[
            gr.Image(type="pil", label="Image de la carte d'électeur"),
            gr.Textbox(label="Numéro de carte"),
        ],
        outputs=gr.Textbox(label="Résultat"),
        title="Vérification de Carte d'Électeur",
        description="Uploadez une image de votre carte d'électeur et entrez son numéro pour vérification",
    )

    return interface


if __name__ == "__main__":

    # Créer et lancer l'interface
    demo = create_interface()
    demo.launch()
