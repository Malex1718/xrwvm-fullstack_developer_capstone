# djangoapp/views.py
from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import logout
from django.contrib import messages
from datetime import datetime
from django.http import JsonResponse
from django.contrib.auth import login, authenticate
import logging
import json
from django.views.decorators.csrf import csrf_exempt
from .models import CarMake, CarModel
from .populate import initiate
from .restapis import get_request, analyze_review_sentiments, post_review

# Get an instance of a logger
logger = logging.getLogger(__name__)

# Vista existente para la página principal
def get_cars(request):
    count = CarMake.objects.filter().count()
    print(count)
    if count == 0:
        initiate()
    car_models = CarModel.objects.select_related('car_make')
    cars = []
    for car_model in car_models:
        cars.append({"CarModel": car_model.name, "CarMake": car_model.car_make.name})
    return JsonResponse({"CarModels": cars})

# Vista para obtener todas las concesionarias o filtrar por estado
def get_dealerships(request, state="All"):
    """
    Obtiene la lista de concesionarias, todas o filtradas por estado
    """
    if state == "All":
        endpoint = "/fetchDealers"
    else:
        endpoint = "/fetchDealers/" + state
    
    dealerships = get_request(endpoint)
    
    if dealerships:
        return JsonResponse({"status": 200, "dealers": dealerships})
    else:
        return JsonResponse({"status": 404, "message": "No dealerships found"})

# Vista para obtener detalles de una concesionaria específica
def get_dealer_details(request, dealer_id):
    """
    Obtiene los detalles de una concesionaria específica por su ID
    """
    if dealer_id:
        endpoint = "/fetchDealer/" + str(dealer_id)
        dealership = get_request(endpoint)
        
        if dealership:
            return JsonResponse({"status": 200, "dealer": dealership})
        else:
            return JsonResponse({"status": 404, "message": "Dealer not found"})
    else:
        return JsonResponse({"status": 400, "message": "Bad Request"})

# Vista para obtener las reseñas de una concesionaria
def get_dealer_reviews(request, dealer_id):
    """
    Obtiene todas las reseñas de una concesionaria y analiza su sentimiento
    """
    if dealer_id:
        endpoint = "/fetchReviews/dealer/" + str(dealer_id)
        reviews = get_request(endpoint)
        
        if reviews:
            # Analizar el sentimiento de cada reseña
            for review_detail in reviews:
                if 'review' in review_detail:
                    # Analizar sentimiento
                    response = analyze_review_sentiments(review_detail['review'])
                    print(f"Sentiment analysis response: {response}")
                    
                    # Agregar el sentimiento al diccionario de la reseña
                    if response:
                        review_detail['sentiment'] = response.get('sentiment', 'neutral')
                    else:
                        review_detail['sentiment'] = 'neutral'
            
            return JsonResponse({"status": 200, "reviews": reviews})
        else:
            return JsonResponse({"status": 200, "reviews": []})
    else:
        return JsonResponse({"status": 400, "message": "Bad Request"})

# Vista para agregar una nueva reseña
@csrf_exempt
def add_review(request):
    """
    Agrega una nueva reseña de un usuario autenticado
    """
    if request.method == "POST":
        # Verificar si el usuario está autenticado
        if not request.user.is_anonymous:
            try:
                # Parsear el cuerpo de la petición
                data = json.loads(request.body)
                
                # Agregar el nombre del usuario a los datos
                data['name'] = request.user.username
                
                # Agregar timestamp si no está presente
                if 'purchase_date' not in data:
                    data['purchase_date'] = datetime.now().isoformat()
                
                # Enviar la reseña al backend
                response = post_review(data)
                
                if response:
                    return JsonResponse({"status": 200, "message": "Review posted successfully"})
                else:
                    return JsonResponse({"status": 500, "message": "Error in posting review"})
                    
            except json.JSONDecodeError:
                return JsonResponse({"status": 400, "message": "Invalid JSON data"})
            except Exception as e:
                print(f"Error adding review: {e}")
                return JsonResponse({"status": 401, "message": "Error in posting review"})
        else:
            return JsonResponse({"status": 403, "message": "Unauthorized - Please login to post a review"})
    else:
        return JsonResponse({"status": 405, "message": "Method not allowed"})

# Vista de login (si no existe)
@csrf_exempt
def login_user(request):
    """
    Autentica y loguea a un usuario
    """
    if request.method == "POST":
        data = json.loads(request.body)
        username = data['userName']
        password = data['password']
        user = authenticate(username=username, password=password)
        
        if user is not None:
            login(request, user)
            response_data = {"userName": username, "status": "Authenticated"}
        else:
            response_data = {"userName": username, "status": "Failed"}
        
        return JsonResponse(response_data)
    
    return JsonResponse({"status": "Method not allowed"})

# Vista de logout
def logout_request(request):
    """
    Desloguea al usuario actual
    """
    logout(request)
    return JsonResponse({"userName": "", "status": "Logged out"})

# Vista de registro (si no existe)
@csrf_exempt
def register_user(request):
    """
    Registra un nuevo usuario
    """
    if request.method == "POST":
        data = json.loads(request.body)
        username = data['userName']
        password = data['password']
        first_name = data['firstName']
        last_name = data['lastName']
        email = data['email']
        
        try:
            # Verificar si el usuario ya existe
            User.objects.get(username=username)
            return JsonResponse({"userName": username, "error": "Already Registered"})
        except User.DoesNotExist:
            # Crear nuevo usuario
            user = User.objects.create_user(
                username=username,
                first_name=first_name,
                last_name=last_name,
                password=password,
                email=email
            )
            login(request, user)
            return JsonResponse({"userName": username, "status": "Authenticated"})
    
    return JsonResponse({"status": "Method not allowed"})