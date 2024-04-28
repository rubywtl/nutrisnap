from flask import Flask, request, jsonify
from flask_cors import CORS
import base64
import pytesseract
from PIL import Image
from io import BytesIO
from main import ocr_scan
from openai import OpenAI
import os
from dotenv import load_dotenv, dotenv_values 
import joblib

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import confusion_matrix, accuracy_score, classification_report
import seaborn as sns
import matplotlib.pyplot as plt

# Instantiate the app
app = Flask(__name__)
CORS(app)

# Initialize OpenAI client
openai = OpenAI() 

load_dotenv() 

# Route for uploading image
@app.route('/extract_text', methods=['POST'])
def extract_text():
    try:
        if 'image' in request.files:
            # Handle image uploaded from file
            image_file = request.files['image']
            image = Image.open(image_file)
            #image = Image.open(image_file)
        elif 'imageDataURL' in request.json:
            # Handle image data URL (e.g., captured from camera)
            imageDataURL = request.json['imageDataURL']
            image_data = base64.b64decode(imageDataURL.split(',')[1])
            image = Image.open(BytesIO(image_data))
             # Handle image data URL (e.g., captured from camera)
        else:
            return jsonify({'error': 'No image data provided'}), 400
        
        # Perform OCR using Tesseract
        extracted_text = pytesseract.image_to_string(image) #, config=myconfig
        # myconfig = r"--psm 11 --oem 3"
        #extracted_text = pytesseract.image_to_string(image)
        cleaned_text = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "fix spelling mistakes and dont say other stuff"},
                {"role": "user", "content": extracted_text}
            ]
        ).choices[0].message.content

        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "summarize this product label in different points (numbered). and add extra information when needed. btw don't add period after the number"},
                {"role": "user", "content": cleaned_text}
            ]
        )
        summary =  response.choices[0].message.content

        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "are there any allergy information i need to make sure"},
                {"role": "user", "content": cleaned_text}
            ]
        )
        allergy =  response.choices[0].message.content

        # Load the trained model
        rf_classifier = joblib.load('random_forest_model.pkl')
        tfidf_vectorizer = joblib.load('tfidf_vectorizer.pkl')
        input_data = cleaned_text
        input_name = "product"
        input_text = input_name + " " + input_data
        # Convert text features into numerical format using the same TF-IDF vectorizer
        X_input_tfidf = tfidf_vectorizer.transform([input_text])
        # Make prediction
        prediction = rf_classifier.predict(X_input_tfidf)[0]
        if(prediction==4):
            prediction_text = "ultra-processed foods"
        elif(prediction==3):
            prediction_text = "processed culinary ingredients"
        elif(prediction==2):
            prediction_text = "processed culinary ingredients"
        elif(prediction==1):
            prediction_text = "minimally-processed ingredients"
        

        return jsonify({'text': cleaned_text, 'summary': summary, 'allergy':allergy, 'prediction': prediction_text})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
