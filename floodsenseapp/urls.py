# floodsenseapp/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path("", views.welcome, name="welcome"),
    path("predict/", views.predict, name="predict"),

    path("chatbot/", views.chatbot, name="chatbot"),

    path('api/get-location-data/', views.get_location_data, name='get_location_data'),


    path('feedback/', views.feedback, name='feedback'),
    path('feedback/submit/', views.submit_feedback, name='submit_feedback'),


    path("home/", views.home, name="home"),

    path('imgupload/', views.imgupload, name="imgupload"),
    path("gallery/", views.gallery, name="gallery"),
    path("contact/", views.contact, name="contact"),
    path('faq/', views.faq, name='faq'),

    path('user_login/', views.user_login, name='user_login'),
    path('user_logout/', views.user_logout, name='user_logout'),
    path('user_register/', views.user_register, name='user_register'),
]
