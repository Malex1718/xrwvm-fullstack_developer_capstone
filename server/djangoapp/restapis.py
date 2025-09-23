# djangoapp/restapis.py
import requests
import json
from .models import CarDealer, DealerReview
from requests.auth import HTTPBasicAuth
import os
from dotenv import load_dotenv

load_dotenv()

backend_url = os.getenv('backend_url', default="http://localhost:3030")
sentiment_analyzer_url = os.getenv('sentiment_analyzer_url', default="http://localhost:5000/")

def get_request(endpoint, **kwargs):
    """
    Realiza una petición GET al backend
    Args:
        endpoint: El endpoint de la API a llamar
        **kwargs: Parámetros adicionales para la URL
    Returns:
        JSON response o None si hay error
    """
    params = ""
    if kwargs:
        for key, value in kwargs.items():
            params = params + key + "=" + str(value) + "&"
    
    request_url = backend_url + endpoint + "?" + params
    print("GET from {} ".format(request_url))
    
    try:
        # Call get method of requests library with URL and parameters
        response = requests.get(request_url)
        return response.json()
    except Exception as e:
        # If any error occurs
        print(f"Network exception occurred: {e}")
        return None

def analyze_review_sentiments(text):
    """
    Analiza el sentimiento de un texto usando el microservicio
    Args:
        text: El texto a analizar
    Returns:
        Dict con el sentimiento o None si hay error
    """
    request_url = sentiment_analyzer_url + "analyze/" + text
    
    try:
        # Call get method of requests library with URL
        response = requests.get(request_url)
        return response.json()
    except Exception as err:
        print(f"Unexpected {err=}, {type(err)=}")
        print("Network exception occurred")
        return {"sentiment": "neutral"}

def post_review(data_dict):
    """
    Publica una nueva reseña en el backend
    Args:
        data_dict: Diccionario con los datos de la reseña
    Returns:
        JSON response o None si hay error
    """
    request_url = backend_url + "/insert_review"
    
    try:
        response = requests.post(request_url, json=data_dict)
        print(response.json())
        return response.json()
    except Exception as e:
        print(f"Network exception occurred: {e}")
        return None