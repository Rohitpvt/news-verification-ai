from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import requests
import json
try:
    import pytesseract
    from PIL import Image
    import io
except ImportError:
    pytesseract = None
    Image = None

app = Flask(__name__, template_folder="templates", static_folder="static")
CORS(app)

@app.route("/")
def index():
    try:
        return render_template("index.html")
    except Exception as e:
        return {"error": str(e)}, 500

@app.route("/api/verify-text", methods=["POST"])
def verify_text():
    try:
        data = request.get_json()
        claim = data.get("claim", "")
        if not claim:
            return {"error": "No claim provided"}, 400
        
        results = [
            {
                "source": "Verification API",
                "coverage": f"Analyzed claim: {claim[:100]}...",
                "verdict": "NEUTRAL",
                "confidence": 0.5
            }
        ]
        return {"results": results}
    except Exception as e:
        return {"error": str(e)}, 500

@app.route("/api/verify-image", methods=["POST"])
def verify_image():
    try:
        if "image" not in request.files:
            return {"error": "No image provided"}, 400
        
        file = request.files["image"]
        if file.filename == "":
            return {"error": "No selected file"}, 400
        
        extracted_text = "[Image OCR would extract text here]"
        if pytesseract and Image:
            try:
                img = Image.open(io.BytesIO(file.read()))
                extracted_text = pytesseract.image_to_string(img)
            except:
                pass
        
        results = [
            {
                "source": "Image Verification",
                "coverage": "Image analyzed",
                "verdict": "NEUTRAL",
                "confidence": 0.5
            }
        ]
        return {"extracted_text": extracted_text, "results": results}
    except Exception as e:
        return {"error": str(e)}, 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
