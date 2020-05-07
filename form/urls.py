from django.urls import path
from .import views

urlpatterns = [
    path('', views.start_xero_auth_view, name='form-startAuth'),
    path('logged/', views.process_callback_view, name='form-callBack'),
    path('logged/sendForm', views.formDataFromHtml, name='form-sendForm'),
]