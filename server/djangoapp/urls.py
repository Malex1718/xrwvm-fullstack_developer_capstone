# djangoapp/urls.py
from django.urls import path
from django.conf.urls.static import static
from django.conf import settings
from . import views

app_name = 'djangoapp'

urlpatterns = [
    # Rutas para autenticación
    path('login', views.login_user, name='login'),
    path('logout', views.logout_request, name='logout'),
    path('register', views.register_user, name='register'),
    
    # Rutas para coches
    path('get_cars', views.get_cars, name='get_cars'),
    
    # Rutas para concesionarias
    path('get_dealers', views.get_dealerships, name='get_dealers'),
    path('get_dealers/<str:state>', views.get_dealerships, name='get_dealers_by_state'),
    
    # Ruta para detalles de concesionaria
    path('dealer/<int:dealer_id>', views.get_dealer_details, name='dealer_details'),
    
    # Ruta para reseñas de concesionaria
    path('reviews/dealer/<int:dealer_id>', views.get_dealer_reviews, name='dealer_reviews'),
    
    # Ruta para agregar reseña
    path('add_review', views.add_review, name='add_review'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)