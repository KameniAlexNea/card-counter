import gradio as gr
from PIL import Image
import os
import sqlite3
from groq import Groq
import io
import base64


def initialize_database():
    db_connection = sqlite3.connect("voter_cards.db")
    cursor = db_connection.cursor()
    cursor.execute(
        """
    CREATE TABLE IF NOT EXISTS voter_cards (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        card_number TEXT UNIQUE
    )
    """
    )
    db_connection.commit()
    return db_connection, cursor


# Configuration GroqCloud
def initialize_groq():
    return Groq(
        api_key=os.getenv("GROQ_API_KEY"),
    )


def encode_image_to_base64(image: Image.Image):
    """Convert a PIL image to a base64-encoded string."""
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    buffer.seek(0)
    return base64.b64encode(buffer.getvalue()).decode("utf-8")


class VoterCardVerifier:
    def __init__(self):
        self.connection, self.cursor = initialize_database()
        self.groq = initialize_groq()

    def verify_card(self, image, card_number):
        # Convertir l'image pour Groq
        if isinstance(image, str):
            image = Image.open(image)
        image = encode_image_to_base64(image)

        # Préparer la requête pour le modèle
        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": f"Vérifie si le numéro {card_number} est clairement visible et lisible sur l'image de cette carte d'électeur."
                        " Confirme également que cette carte est bien d'origine camerounaise en vérifiant la présence explicite de la mention 'Cameroun' sur la carte."
                        " Réponds uniquement par 'true' ou 'false' : 'true' si le numéro est présent, lisible, et que la carte est d'origine camerounaise ; 'false' dans tous les autres cas.",
                    },
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/PNG;base64,{image}"},
                    },
                ],
            },
        ]

        # Appeler le modèle
        response = self.groq.chat.completions.create(
            model=os.getenv("GROQ_MODEL_ID"),
            messages=messages,
            temperature=0.1,
            max_tokens=25,
        )
        result = response.choices[0].message.content.strip().lower()
        print(result)
        is_valid = "true" in result

        if is_valid:
            # Sauvegarder dans Firebase
            return self.save_card_number(card_number)
        else:
            return "Numéro de carte non trouvé sur l'image"

    def save_card_number(self, card_number):
        # Ajouter le numéro à Firestore
        # Sauvegarder dans la base de données
        try:
            self.cursor.execute(
                "INSERT INTO voter_cards (card_number) VALUES (?)", (card_number,)
            )
            self.connection.commit()
            return f"Numéro vérifié et sauvegardé : {card_number}"
        except sqlite3.IntegrityError:
            return f"Le numéro {card_number} existe déjà dans la base."


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
