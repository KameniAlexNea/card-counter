import os

from dotenv import load_dotenv

load_dotenv(override=True)

import io
import os
from typing import Union

import easyocr
import firebase_admin
import gradio as gr
from firebase_admin import credentials, firestore
from loguru import logger
from PIL import Image
from thefuzz import fuzz

from processor import ImageHandler, PreprocessingConfig, ProcessedImage


class EasyOCRReader:
    def __init__(self):
        self.reader = easyocr.Reader(["fr", "en"], gpu=False)
        self.process = ImageHandler()
        self.config = PreprocessingConfig()

    def chat(self, image):
        processed: ProcessedImage = self.process.preprocess_image(image, self.config)
        image = Image.fromarray(processed.image)
        # Convert image to bytes
        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format="PNG")
        img_byte_arr = img_byte_arr.getvalue()

        # Call readtext with image bytes
        texts = self.reader.readtext(img_byte_arr, detail=0)
        logger.info(" ".join(texts))
        return texts


class FirebaseConnector:
    def get_config(self):
        return {
            "type": os.getenv("type"),
            "project_id": os.getenv("project_id"),
            "private_key_id": os.getenv("private_key_id"),
            "private_key": os.getenv("private_key").replace("\\n", "\n"),
            "client_email": os.getenv("client_email"),
            "client_id": os.getenv("client_id"),
            "auth_uri": os.getenv("auth_uri"),
            "token_uri": os.getenv("token_uri"),
            "auth_provider_x509_cert_url": os.getenv("auth_provider_x509_cert_url"),
            "client_x509_cert_url": os.getenv("client_x509_cert_url"),
            "universe_domain": os.getenv("universe_domain"),
        }

    def __init__(self):
        # print(os.environ)
        firebase_config = self.get_config()
        cred = credentials.Certificate(firebase_config)
        firebase_admin.initialize_app(cred)
        self.db = firestore.client()
        self.collecttion_name = os.getenv("collection", "id-card")

    def add(self, ocr: str, key: str):
        doc_ref = self.db.collection(self.collecttion_name).document(key)
        if doc_ref.get().exists:
            raise ValueError(f"Document with key {key} already exists.")
        return self.db.collection(self.collecttion_name).add({"ocr": ocr}, document_id=key)

    def get_id_counted(self):
        docs = self.db.collection(self.collecttion_name).stream()
        count = sum(1 for _ in docs)
        return count


def search_element(words: list[str], target: str, thr: float = 60):
    scores = list(map(lambda x: fuzz.partial_ratio(x, target), words))
    word_scores = [(w, s) for w, s in zip(words, scores) if s >= thr]
    return word_scores


class VoterCardVerifier:
    def __init__(self):
        self.db = FirebaseConnector()
        self.ocr_engine = EasyOCRReader()
        self.thr = int(os.getenv("thr", 75))
        self.n_cards = 0

    def verify_card(self, image: Union[str, Image.Image], card_number,):
        self.n_cards = self.get_id_counted()
        # Convertir l'image pour Groq
        if isinstance(image, str):
            image = Image.open(image)

        # Préparer la requête pour le modèle et l'appeler
        ocr_data = self.ocr_engine.chat(image)

        score1 = search_element(ocr_data, "camer", self.thr)
        score2 = search_element(ocr_data, card_number, self.thr)

        ocr_data = score1 + score2
        logger.info(str(ocr_data))

        # valider les entrées
        is_valid = len(score1) and len(score2)
        try:
            if is_valid:
                # Sauvegarder dans Firebase
                self.save_card_number(ocr_data, card_number)
                self.n_cards += 1
                return f"Your ID Card have been recorded, thank you !!! Num Card: {self.n_cards}"
            else:
                return f"Card number not found, please improve the quality of image passed. Num Card: {self.n_cards}"
        except ValueError as ex:
            return f"ID Card already saved in the database. Num Card: {self.n_cards}"

    def save_card_number(self, ocr_data, card_number):
        return self.db.add(str(ocr_data), str(card_number))

    def get_id_counted(self):
        return self.db.get_id_counted()


# Interface Gradio
def create_interface():
    verifier = VoterCardVerifier()
    description = (
        "Card ID Counter is an application designed to count voter card numbers "
        "by analyzing uploaded images using OCR technology. It ensures accuracy by "
        "checking if the provided number appears on the card and confirming its from Cameroon.\n\n"
        "🌟 **Code Repository**: [Card ID Counter GitHub](https://github.com/Nganga-AI/card-counter)"
    )

    def process(image, card_number: str):
        if not card_number.strip():
            return "Enter your elect count number"
        return verifier.verify_card(image, card_number)

    interface = gr.Interface(
        fn=process,
        inputs=[
            gr.Image(type="pil", label="Upload ID Card Image"),
            gr.Textbox(label="Card Number"),
        ],
        outputs=gr.Textbox(label="Result"),
        title="Voters ID Counter",
        description=description,
    )

    return interface


if __name__ == "__main__":
    # Créer et lancer l'interface
    demo = create_interface()
    demo.launch()
