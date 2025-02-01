# Card ID Counter

## Overview

**Card ID Counter** is a web-based application for verifying voter card numbers using Optical Character Recognition (OCR) and a database for storage. Users upload an image of their voter card along with the card number, and the application verifies:

1. If the provided number appears on the card.
2. If the card is of Cameroonian origin (by checking for the presence of "Cameroun" on the card).

If verification is successful, the card number is stored in a Firebase database.

## Features

* **OCR-based Verification** : Uses EasyOCR to extract text from the voter card image.
* **Database Integration** : Stores verified card numbers in Firebase, ensuring uniqueness.
* **User-Friendly Interface** : Built with Gradio for easy interaction.
* **Fuzzy Matching** : Uses fuzzy string matching to improve number recognition accuracy.

## Installation and Setup

### Prerequisites

1. Python 3.8 or later.
2. Required Python packages:
   * `gradio`
   * `pillow`
   * `easyocr`
   * `firebase-admin`
   * `thefuzz`
   * `python-dotenv`

### Steps

1. Clone this repository:
   ```bash
   git clone git@github.com:Nganga-AI/card-counter.git
   cd card-id-counter
   ```
2. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```
3. Set up Firebase credentials:
   * Create a `.env` file in the root directory and add your Firebase service account credentials:
     ```env
     type="service_account"
     project_id="your-project-id"
     private_key_id="your-private-key-id"
     private_key="your-private-key"
     client_email="your-client-email"
     client_id="your-client-id"
     auth_uri="https://accounts.google.com/o/oauth2/auth"
     token_uri="https://oauth2.googleapis.com/token"
     auth_provider_x509_cert_url="https://www.googleapis.com/oauth2/v1/certs"
     client_x509_cert_url="your-client-x509-cert-url"
     universe_domain="googleapis.com"
     ```
4. Run the application:
   ```bash
   gradio app.py
   ```

## How It Works

1. **Initialization** :
   * Firebase is initialized using service account credentials.
   * The OCR engine (EasyOCR) is loaded for text extraction.
2. **User Interaction** :
   * Users upload an image of their voter card and enter the card number via Gradio.
   * The image is processed, and text is extracted using OCR.
3. **Verification** :
   * The OCR result is searched for:
     1. The provided card number.
     2. The keyword "Cameroun" to confirm its origin.
   * Fuzzy matching is applied to handle OCR errors.
4. **Database Storage** :
   * If verification succeeds, the card number is stored in Firebase, avoiding duplicates.
5. **Output** :
   * Users receive feedback on whether the verification was successful or failed.

## Project Structure

```
card-id-counter/
│
├── app.py               # Main application file
├── processor.py         # Image processing module
├── requirements.txt     # Python dependencies
├── .env                 # Environment variables for Firebase
├── README.md            # Project documentation
```

## Usage

1. Open the application in your browser after launching it.
2. Upload an image of your voter card.
3. Enter the voter card number.
4. View the result of the verification.

## Notes

* Ensure the uploaded image is clear and readable.
* This application is tailored for verifying voter cards specific to Cameroon.

## Future Enhancements

* Improved OCR preprocessing for better accuracy.
* Support for additional countries and card types.
* Alternative verification models using machine learning.

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.

## Acknowledgments

* [EasyOCR](https://www.jaided.ai/easyocr/) for text extraction.
* [Firebase](https://firebase.google.com/) for database storage.
* [Gradio](https://www.gradio.app/) for the user-friendly web interface.

---

For any questions or issues, feel free to open an issue in the repository.
