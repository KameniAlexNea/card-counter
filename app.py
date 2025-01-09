import gradio as gr
from PIL import Image
import sqlite3
from ocr_engine import ocr_model


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
    db_connection.close()


class VoterCardVerifier:
    def __init__(self):
        initialize_database()
    
    def verify_card(self, image, card_number):
        # Convertir l'image pour Groq
        if isinstance(image, str):
            image = Image.open(image)

        # Préparer la requête pour le modèle et l'appeler
        message = ocr_model.chat(image).strip().lower()

        # valider les entrées
        is_valid = ("camer" in message) and (card_number in message)

        if is_valid:
            # Sauvegarder dans Firebase
            return self.save_card_number(card_number)
        else:
            return "Numéro de carte non trouvé sur l'image"

    def save_card_number(self, card_number):
        db_connection = sqlite3.connect("voter_cards.db")
        cursor = db_connection.cursor()
        # Ajouter le numéro à Firestore
        # Sauvegarder dans la base de données
        try:
            cursor.execute(
                "INSERT INTO voter_cards (card_number) VALUES (?)", (card_number,)
            )
            db_connection.commit()
            return f"Numéro vérifié et sauvegardé : {card_number}"
        except sqlite3.IntegrityError:
            return f"Le numéro {card_number} existe déjà dans la base."
        finally:
            db_connection.close()


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
