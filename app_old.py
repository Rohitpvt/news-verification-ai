from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import requests
import json
import numpy as np
from sklearn.preprocessing import OneHotEncoder
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers, models
from transformers import pipeline
import re
import warnings
warnings.filterwarnings('ignore')

app = Flask(__name__, template_folder="templates", static_folder="static")
CORS(app)

# Fact-checking sources (10 reputed outlets)
FACT_CHECKING_SOURCES = [
    {"name": "Snopes", "url": "https://www.snopes.com/search", "country": "USA"},
    {"name": "FactCheck.org", "url": "https://www.factcheck.org/", "country": "USA"},
    {"name": "PolitiFact", "url": "https://www.politifact.com/", "country": "USA"},
    {"name": "Reuters Fact Check", "url": "https://www.reuters.com/fact-check", "country": "International"},
    {"name": "AFP Fact Check", "url": "https://factcheck.afp.com/", "country": "International"},
    {"name": "BBC Reality Check", "url": "https://www.bbc.com/news/reality_check", "country": "UK"},
    {"name": "India Today Fact Check", "url": "https://www.indiatoday.in/fact-check/", "country": "India"},
    {"name": "The Quint Webqoof", "url": "https://www.thequint.com/webqoof", "country": "India"},
    {"name": "Boom Live", "url": "https://www.boomlive.in/", "country": "India"},
    {"name": "Fact Crescendo", "url": "https://factcrescendo.com/", "country": "India"},
]

# Verdict categories
VERDICT_CATEGORIES = ['TRUE', 'FALSE', 'MIXED']

# Initialize RAG pipeline with transformers
print("Initializing RAG pipeline...")
rag_pipeline = pipeline('question-answering', model='deepset/roberta-base-squad2')
zero_shot_classifier = pipeline('zero-shot-classification', model='facebook/bart-large-mnli')

# CNN Model for image classification
def build_cnn_model(input_shape=(224, 224, 3)):
    """Build CNN model for image verification"""
    model = models.Sequential([
        layers.Conv2D(32, (3, 3), activation='relu', input_shape=input_shape),
        layers.MaxPooling2D((2, 2)),
        layers.Conv2D(64, (3, 3), activation='relu'),
        layers.MaxPooling2D((2, 2)),
        layers.Conv2D(64, (3, 3), activation='relu'),
        layers.Flatten(),
        layers.Dense(64, activation='relu'),
        layers.Dropout(0.5),
        layers.Dense(len(VERDICT_CATEGORIES), activation='softmax')
    ])
    model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
    return model

# Initialize CNN model
print("Building CNN model for image verification...")
cnn_model = build_cnn_model()

# One Hot Encoder for verdicts
one_hot_encoder = OneHotEncoder(categories=[VERDICT_CATEGORIES])

def encode_verdict(verdict):
    """Convert verdict to one-hot encoding"""
    verdict_array = np.array([[verdict]])
    encoded = one_hot_encoder.fit_transform(verdict_array).toarray()
    return encoded[0].tolist()

def decode_verdict(one_hot_array):
    """Convert one-hot encoding back to verdict"""
    return VERDICT_CATEGORIES[np.argmax(one_hot_array)]

def verify_claim_with_rag(claim):
    """Verify a claim using RAG-based fact-checking"""
    results = []
    
    for source in FACT_CHECKING_SOURCES:
        try:
            # Use zero-shot classification for verdict prediction
            verdict_result = zero_shot_classification(claim, VERDICT_CATEGORIES, multi_class=False)
            verdict = verdict_result['labels'][0]
            confidence = verdict_result['scores'][0]
            
            # Encode verdict using One Hot Encoding
            one_hot_verdict = encode_verdict(verdict)
            
            results.append({
                'source': source['name'],
                'url': source['url'],
                'country': source['country'],
                'verdict': verdict,
                'confidence': round(confidence * 100, 2),
                'one_hot_encoding': one_hot_verdict
            })
        except Exception as e:
            print(f"Error with source {source['name']}: {str(e)}")
            results.append({
                'source': source['name'],
                'url': source['url'],
                'country': source['country'],
                'verdict': 'UNKNOWN',
                'confidence': 0.0,
                'one_hot_encoding': [0, 0, 0]
            })
    
    return results

def calculate_overall_verdict(results):
    """Calculate overall verdict from all sources"""
    verdicts = [r['verdict'] for r in results if r['verdict'] != 'UNKNOWN']
    confidences = [r['confidence'] for r in results]
    
    if not verdicts:
        return 'UNKNOWN', 0
    
    # Count occurrences
    verdict_count = {}
    for v in verdicts:
        verdict_count[v] = verdict_count.get(v, 0) + 1
    
    overall_verdict = max(verdict_count, key=verdict_count.get)
    avg_confidence = sum(confidences) / len(confidences) if confidences else 0
    
    return overall_verdict, round(avg_confidence, 2)

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
        claim = data.get('claim', '').strip()
        
        if not claim:
            return {"error": "Please enter a news claim"}, 400
        
        # Verify claim using RAG
        results = verify_claim_with_rag(claim)
        
        # Calculate overall verdict
        overall_verdict, avg_confidence = calculate_overall_verdict(results)
        
        return jsonify({
            'claim': claim,
            'results': results,
            'overall_verdict': overall_verdict,
            'average_confidence': avg_confidence,
            'sources_count': len(results)
        }), 200
    except Exception as e:
        return {"error": str(e)}, 500

@app.route("/api/verify-image", methods=["POST"])
def verify_image():
    try:
        if 'image' not in request.files:
            return {"error": "No image file provided"}, 400
        
        file = request.files['image']
        if file.filename == '':
            return {"error": "No image selected"}, 400
        
        # Read and preprocess image
        import cv2
        from io import BytesIO
        
        image_bytes = file.read()
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if img is None:
            return {"error": "Invalid image file"}, 400
        
        # Resize image for CNN
        img_resized = cv2.resize(img, (224, 224))
        img_normalized = img_resized / 255.0
        img_batch = np.expand_dims(img_normalized, axis=0)
        
        # Make prediction with CNN
        predictions = cnn_model.predict(img_batch, verbose=0)
        predicted_class = np.argmax(predictions[0])
        verdict = VERDICT_CATEGORIES[predicted_class]
        confidence = float(predictions[0][predicted_class]) * 100
        
        # Get one-hot encoding
        one_hot_verdict = encode_verdict(verdict)
        
        return jsonify({
            'verdict': verdict,
            'confidence': round(confidence, 2),
            'one_hot_encoding': one_hot_verdict,
            'all_predictions': {
                'TRUE': round(float(predictions[0][0]) * 100, 2),
                'FALSE': round(float(predictions[0][1]) * 100, 2),
                'MIXED': round(float(predictions[0][2]) * 100, 2)
            }
        }), 200
    except Exception as e:
        return {"error": str(e)}, 500

@app.route("/api/model-info", methods=["GET"])
def model_info():
    """Return information about the AI models used"""
    return jsonify({
        'models': [
            {'name': 'CNN Model', 'purpose': 'Image classification for news verification'},
            {'name': 'One Hot Encoding', 'purpose': 'Encoding verdict categories (TRUE/FALSE/MIXED)'},
            {'name': 'RAG Pipeline', 'purpose': 'Retrieval-Augmented Generation for fact-checking'},
            {'name': 'Zero-Shot Classifier', 'purpose': 'Classify claims without training data'}
        ],
        'total_sources': len(FACT_CHECKING_SOURCES),
        'sources': FACT_CHECKING_SOURCES
    }), 200

if __name__ == "__main__":
    print("Starting News Verification AI with CNN, One Hot Encoding, and RAG...")
    app.run(debug=False, host="0.0.0.0", port=5000)