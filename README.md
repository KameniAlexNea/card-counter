# Voter Card Verification System

## Overview

This project is a web-based application for verifying voter card numbers using machine learning and database storage. Users upload an image of their voter card along with the card number. The application uses GroqCloud's LLM to verify:

1. If the provided number appears on the card.
2. If the card is of Cameroonian origin (by checking for the presence of "Cameroun" on the card).

If the verification is successful, the card number is saved in a local SQLite database.

## Features

* **Image and Text Verification** : Validates the voter card number and checks the origin of the card using GroqCloud's LLM with vision capabilities.
* **Database Integration** : Stores verified card numbers in a SQLite database, ensuring uniqueness.
* **User-Friendly Interface** : Provides an intuitive interface built with Gradio for easy interaction.

## Installation and Setup

### Prerequisites

1. Python 3.8 or later.
2. Required Python packages:
   * `gradio`
   * `pillow`
   * `sqlite3` (part of Python's standard library)
   * `groq` (GroqCloud Python SDK)
   * `base64` (part of Python's standard library)

### Steps

1. Clone this repository:
   ```bash
   git clone https://github.com/your-repo/voter-card-verification.git
   cd voter-card-verification
   ```
2. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```
3. Set up your GroqCloud API key:
   * Add your GroqCloud API key as an environment variable:
     ```bash
     export GROQ_API_KEY="your-api-key"
     ```
   * Specify the model ID as an environment variable:
     ```bash
     export GROQ_MODEL_ID="llama-3.2-11b-vision-preview"
     ```
4. Run the application:
   ```bash
   python app.py
   ```

## How It Works

1. **Initialization** :

* A SQLite database (`voter_cards.db`) is created to store voter card numbers.
* The GroqCloud client is initialized using the API key.

1. **User Interaction** :

* Users upload an image of their voter card and enter the card number in the Gradio interface.
* The image is converted to a base64-encoded string to send to the GroqCloud LLM.

1. **Verification** :

* The GroqCloud LLM is queried to check if:
  1. The provided number appears on the card.
  2. The card contains the word "Cameroun" to confirm its origin.
* The model responds with `true` if both conditions are met; otherwise, it responds with `false`.

1. **Database Storage** :

* If verification succeeds, the card number is stored in the SQLite database. Duplicate entries are prevented.

1. **Output** :

* Users receive feedback on whether the verification succeeded or failed.

## Project Structure

```
voter-card-verification/
│
├── app.py               # Main application file
├── requirements.txt     # Python dependencies
├── voter_cards.db       # SQLite database (auto-created on first run)
└── README.md            # Project documentation
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

* Integration with Firebase for cloud-based storage.
* Improved OCR fallback for local verification.
* Support for additional countries and card types.

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.

## Acknowledgments

* [GroqCloud](https://www.groq.com/) for their advanced LLM capabilities.
* [Gradio](https://www.gradio.app/) for the user-friendly web interface.

---

For any questions or issues, feel free to open an issue in the repository.
