# djangoapp/microservices/sentiment_analyzer.py
from flask import Flask, request, jsonify
from flask_cors import CORS
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
import os

# Descargar los recursos necesarios de NLTK
nltk.download('vader_lexicon', quiet=True)
nltk.download('punkt', quiet=True)

app = Flask(__name__)
CORS(app)

# Inicializar el analizador de sentimientos
sia = SentimentIntensityAnalyzer()

@app.route('/')
def home():
    """Ruta de verificación del servicio"""
    return jsonify({
        "message": "Sentiment Analyzer Service is running",
        "version": "1.0.0",
        "endpoints": {
            "/": "Service status",
            "/analyze/<text>": "Analyze sentiment of text",
            "/health": "Health check"
        }
    })

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({"status": "healthy"}), 200

@app.route('/analyze/<string:text>', methods=['GET'])
def analyze_sentiment(text):
    """
    Analiza el sentimiento de un texto dado
    Returns: positive, negative o neutral
    """
    try:
        # Decodificar el texto si viene con codificación URL
        import urllib.parse
        text = urllib.parse.unquote(text)
        
        # Analizar el sentimiento usando VADER
        scores = sia.polarity_scores(text)
        
        # Determinar el sentimiento basado en el compound score
        compound = scores['compound']
        
        if compound >= 0.05:
            sentiment = 'positive'
        elif compound <= -0.05:
            sentiment = 'negative'
        else:
            sentiment = 'neutral'
        
        return jsonify({
            'sentiment': sentiment,
            'scores': {
                'positive': scores['pos'],
                'negative': scores['neg'],
                'neutral': scores['neu'],
                'compound': scores['compound']
            },
            'text': text[:100] + '...' if len(text) > 100 else text
        })
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'sentiment': 'neutral'
        }), 500

@app.route('/analyze', methods=['POST'])
def analyze_sentiment_post():
    """
    Analiza el sentimiento de un texto enviado por POST
    """
    try:
        data = request.get_json()
        text = data.get('text', '')
        
        if not text:
            return jsonify({'error': 'No text provided', 'sentiment': 'neutral'}), 400
        
        # Analizar el sentimiento
        scores = sia.polarity_scores(text)
        compound = scores['compound']
        
        if compound >= 0.05:
            sentiment = 'positive'
        elif compound <= -0.05:
            sentiment = 'negative'
        else:
            sentiment = 'neutral'
        
        return jsonify({
            'sentiment': sentiment,
            'scores': scores,
            'text': text[:100] + '...' if len(text) > 100 else text
        })
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'sentiment': 'neutral'
        }), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)