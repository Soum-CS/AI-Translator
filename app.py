import os
import PyPDF2
import pytesseract

from flask import Flask, render_template, request, redirect
from deep_translator import GoogleTranslator
from database import db, History
from langdetect import detect
from gtts import gTTS
from PIL import Image

# --------------------------------------------------
# Tesseract OCR Path
# --------------------------------------------------

pytesseract.pytesseract.tesseract_cmd = (
    r"C:\Program Files\Tesseract-OCR\tesseract.exe"
)

# --------------------------------------------------
# Flask App
# --------------------------------------------------

app = Flask(__name__)

# --------------------------------------------------
# Database Configuration
# --------------------------------------------------

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///translations.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

with app.app_context():
    db.create_all()

# --------------------------------------------------
# Home Route
# --------------------------------------------------

@app.route("/", methods=["GET", "POST"])
def index():

    translated = ""
    detected = ""

    if request.method == "POST":

        try:

            # ------------------------------
            # Get Text
            # ------------------------------

            text = request.form.get("text", "").strip()

            # ------------------------------
            # Target Language
            # ------------------------------

            target = request.form.get("target")

            # ------------------------------
            # Image Upload
            # ------------------------------

            image_file = request.files.get("image")

            # ------------------------------
            # PDF Upload
            # ------------------------------

            pdf_file = request.files.get("pdf")

            # ------------------------------
            # OCR Image Translation
            # ------------------------------

            if image_file and image_file.filename != "":

                image = Image.open(image_file)

                text = pytesseract.image_to_string(image)

            # ------------------------------
            # PDF Translation
            # ------------------------------

            elif pdf_file and pdf_file.filename != "":

                reader = PyPDF2.PdfReader(pdf_file)

                text = ""

                for page in reader.pages:

                    page_text = page.extract_text()

                    if page_text:
                        text += page_text + "\n"

            # ------------------------------
            # Translate
            # ------------------------------

            if text:

                # Detect Language

                detected = detect(text)

                # Translate Text

                translated = GoogleTranslator(
                    source="auto",
                    target=target
                ).translate(text)

                # Save History

                history = History(
                    original=text,
                    translated=translated
                )

                db.session.add(history)
                db.session.commit()

                # Create Static Folder

                os.makedirs(
                    "static",
                    exist_ok=True
                )

                # Generate Speech

                tts = gTTS(translated)

                tts.save(
                    "static/speech.mp3"
                )

            else:

                translated = (
                    "Please enter text "
                    "or upload an image/PDF."
                )

        except Exception as e:

            translated = f"Error: {e}"

    # -----------------------------------
    # Translation History
    # -----------------------------------

    histories = History.query.order_by(
        History.id.desc()
    ).all()

    return render_template(
        "index.html",
        translated=translated,
        detected=detected,
        histories=histories
    )

# --------------------------------------------------
# Clear History
# --------------------------------------------------

@app.route("/clear_history")
def clear_history():

    History.query.delete()

    db.session.commit()

    return redirect("/")

# --------------------------------------------------
# Run App
# --------------------------------------------------

if __name__ == "__main__":

    app.run(
        debug=True
    )

    # redeploy