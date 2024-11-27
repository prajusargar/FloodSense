# floodsenseapp/views.py

from django.shortcuts import render, redirect
from django.http import JsonResponse
import pandas as pd
import pickle
import os, json, time

from datetime import datetime, timedelta
from django.utils.timezone import now, timedelta
from django.utils import timezone
from .models import SensorData, AlertNotifyData, ImgData, ChatData, ReportedFloodAlertData, FeedBackData, FaqData

from django.db.models import Max


import base64
from django.core.files.storage import FileSystemStorage
from PIL import Image
import io


from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout, logout
from django.contrib.auth.decorators import login_required

from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt


import requests
# from timezonefinder import TimezoneFinder
from geopy.geocoders import Nominatim
import pytz

import folium

from django.core.mail import send_mail
from django.conf import settings


import google.generativeai as genai

# Configure Generative AI API
my_secret = "AIzaSyCSOocLk-E0gnA9V_yz0dyeuPZdbD8mjME"
genai.configure(api_key=my_secret)
geminimodel = genai.GenerativeModel(model_name="gemini-1.5-flash")


# Path to model and feature files
MODEL_PATH = os.path.join(os.path.dirname(__file__), "random_forest_flood_model.pkl")
FEATURES_PATH = os.path.join(os.path.dirname(__file__), "feature_names.pkl")

# Load the model and feature names once (global variable to avoid reloading every request)
with open(MODEL_PATH, "rb") as model_file:
    model = pickle.load(model_file)
with open(FEATURES_PATH, "rb") as feature_file:
    feature_names = pickle.load(feature_file)

# # Define your model and feature names here
# feature_names = [
#     "monsoonintensity", "topographydrainage", "rivermanagement", "climatechange",
#     "siltation", "drainagesystems", "coastalvulnerability", "watersheds",
#     "deterioratinginfrastructure", "wetlandloss"
# ]


def welcome(request):
    return render(request, "floodsenseapp/welcome.html")

# def home(request):
#     print(f"MODEL_PATH: {MODEL_PATH}")
#     print(f"FEATURES_PATH: {FEATURES_PATH}")

#     # Create a Folium map centered at Mumbai
#     mumbai_location = [19.0760, 72.8777]
#     my_map = folium.Map(location=mumbai_location, zoom_start=12)

#     # Add a marker for Mumbai
#     folium.Marker(
#         location=mumbai_location,
#         popup="Mumbai",
#         icon=folium.Icon(color="blue", icon="info-sign")
#     ).add_to(my_map)

#     # Save the map as an HTML file
#     map_html = my_map._repr_html_()  # Render map directly as HTML

#     # Handle the `report` query parameter
#     report_id = request.GET.get('report', None)
#     if report_id:
#         reports = ReportedFloodAlertData.objects.filter(report_id=report_id)
#     else:
#         last_24_hours = now() - timedelta(hours=24)
#         reports = ReportedFloodAlertData.objects.filter(timestamp__gte=last_24_hours)

   

#     # Pass the HTML to the template
#     return render(request, 'floodsenseapp/home.html', {'map_html': map_html, 'reports': reports})


def home(request):
    # Mumbai center location
    mumbai_location = [19.0760, 72.8777]
    my_map = folium.Map(location=mumbai_location, zoom_start=12)

    # Fetch unique and latest sensor data by `nodename`
    latest_sensors = (
        SensorData.objects.values('nodename')
        .annotate(latest_timestamp=Max('timestamp'))
        .values('nodename', 'latitude', 'longitude', 'predictionclass', 'predictprobability', 'predicttime', 'timestamp')
    )

    # Add a marker for each unique and latest sensor
    for sensor in latest_sensors:
        print(f"sensor: {sensor}")
        try:
            # Ensure latitude and longitude are convertible to float
            lat = float(sensor['latitude'])
            lon = float(sensor['longitude'])
            popup_info = (
                f"<b>{sensor['nodename']}</b> <br>"
                f"{sensor['predictionclass']}<br>"
                # f"<b>Prediction Probability:</b> {sensor['predictprobability']}<br>"
                # f"<b>Prediction Time:</b> {sensor['predicttime']}<br>"
                # f"<b>Timestamp:</b> {sensor['timestamp']}"
            )
            folium.Marker(
                location=[lat, lon],
                popup=popup_info,
                icon=folium.Icon(color="green", icon="info-sign")
            ).add_to(my_map)
        except ValueError:
            print(f"Invalid latitude or longitude for sensor {sensor['nodename']}")

    # Save the map as an HTML file
    map_html = my_map._repr_html_()  # Render map directly as HTML

    # Handle the `report` query parameter (optional if used elsewhere in the app)
    report_id = request.GET.get('report', None)
    if report_id:
        reports = ReportedFloodAlertData.objects.filter(report_id=report_id)
    else:
        last_24_hours = now() - timedelta(hours=24)
        reports = ReportedFloodAlertData.objects.filter(timestamp__gte=last_24_hours)

    # Pass the HTML to the template
    return render(request, 'floodsenseapp/home.html', {'map_html': map_html, 'reports': reports})



# API to return data for a given location
def get_location_data(request):
    if request.method == "POST":
        location = request.POST.get('location', None)

        # Mock data for the locations
        location_data = {
            "dadar": {"flood_risk": "65%", "rainfall_mm": 200},
            "andheri": {"flood_risk": "62%", "rainfall_mm": 150},
            "virar": {"flood_risk": "58%", "rainfall_mm": 50},
        }

        # Return data for the requested location
        data = location_data.get(location.lower(), {"error": "Location not found"})
        return JsonResponse(data)
    return JsonResponse({"error": "Invalid request method"}, status=400)


def gallery(request):
    nodename = "Prajakta"  # You can change this as needed
    img_data = ImgData.objects.filter(nodename=nodename)  # Retrieve images for the specified nodename

    content = {
            "images": img_data
    }
    return render(request, "floodsenseapp/gallery.html", content)

def contact(request):
    return render(request, "floodsenseapp/contact.html")

# Display FAQ Records
def faq(request):
    faq_records = FaqData.objects.all()
    return render(request, 'floodsenseapp/faq.html', {'faq_records': faq_records})


# Display Feedback
def feedback(request):
    feedback_records = FeedBackData.objects.order_by('-timestamp')[:50]
    return render(request, 'floodsenseapp/feedback.html', {'feedback_records': feedback_records})

# Submit Feedback
@csrf_exempt
def submit_feedback(request):
    if request.method == 'POST':
        topic = request.POST.get('topic', '').strip()
        msg_text = request.POST.get('msg_text', '').strip()
        loggedUser = request.user.username
        
        if topic and msg_text:
            feedback = FeedBackData(topic=topic, username=loggedUser, MsgText=msg_text)
            feedback.save()
            return JsonResponse({'success': 'Feedback submitted successfully.'}, status=200)
        return JsonResponse({'error': 'All fields are required.'}, status=400)
    return render(request, 'floodsenseapp/feedbackform.html')
    

# def get_current_time_and_location():
#     # Get public IP address to determine location
#     ip_data = requests.get("https://ipinfo.io/json").json()
#     lat, lon = map(float, ip_data["loc"].split(","))

#     # Reverse geocode to get location details
#     geolocator = Nominatim(user_agent="geoapi")
#     location = geolocator.reverse((lat, lon), language="en")
#     address = location.address

#     # Get timezone
#     tf = TimezoneFinder()
#     timezone_str = tf.timezone_at(lng=lon, lat=lat)
#     timezone = pytz.timezone(timezone_str)

#     # Get current time in the determined timezone
#     local_time = datetime.now(timezone)

#     return {
#         "address": address,
#         "latitude": lat,
#         "longitude": lon,
#         "timezone": timezone_str,
#         "local_time": local_time.strftime("%Y-%m-%d %H:%M:%S")
#     }

def get_current_time_and_location():
    # Get public IP address to determine location
    ip_data = requests.get("https://ipinfo.io/json").json()
    lat, lon = map(float, ip_data["loc"].split(","))

    # Reverse geocode to get location details
    geolocator = Nominatim(user_agent="geoapi")
    location = geolocator.reverse((lat, lon), language="en")
    address = location.address

    # Get timezone using geopy
    timezone_obj = geolocator.timezone((lat, lon))
    timezone_str = timezone_obj.zone  # Get timezone string

    # Get current time in the determined timezone
    local_time = datetime.now(timezone_obj)

    return {
        "address": address,
        "latitude": lat,
        "longitude": lon,
        "timezone": timezone_str,
        "local_time": local_time.strftime("%Y-%m-%d %H:%M:%S")
    }


# Example usage
# details = get_current_time_and_location()
# print(details)



def chatbot(request):
    if request.method == "POST":
        # Get the chat text from the form
        user_message = request.POST.get("chatText")
        # username = "node"  # Default username for interaction
        loggedUser = request.user.username  
        # Use the logged-in user's username

        # Fetch the latest 6 chats for the user
        latest_chats = ChatData.objects.filter(username=loggedUser).order_by('-timestamp')[:6]

        if latest_chats:
            chat_history = "\n".join([chat.ChatText for chat in reversed(latest_chats)])

        else:
            chat_history = ""

        systemPrompt = f"""
            act as a chat bot that replys to the user quesions where the scope is too specific about topics = [who are you, weather, flood, flood prediction, flood prediction model, flood prediction model, flood prediction model, flood prediction, about developer team, about developer college]
    
            #Developer and Project info:
            ```
            Prajkta Madhukar Sargar and Pranjal girkar and our project mentor is Miss. Neha Athavle Ma'am

            Problem Statement:
            Mumbai, a coastal city, experiences significant challenges due to recurrent flooding caused by heavy rainfall, high tides, and inadequate drainage infrastructure. These floods disrupt daily life, cause extensive damage, and threaten human lives. A predictive system using machine learning can forecast flood occurrences, enabling timely preparedness and mitigation to reduce damage and save lives.
            
            
            Abstract:
            Flooding is a recurring issue in Mumbai, often resulting in economic loss, damage to infrastructure, and endangering lives. This project aims to develop a machine learning-based flood prediction system for Mumbai, using historical and real-time data such as rainfall, tide levels, and drainage capacity. The predictive model will alert relevant authorities and the public, fostering proactive measures. Integrating IoT devices for real-time data collection enhances accuracy and timeliness. The project emphasizes data preprocessing, feature engineering, model development, and deployment as a web API for broader accessibility.
            
            
            Introduction:
            Our approach focuses on leveraging historical data, machine learning techniques, and IoT devices to address Mumbai's flooding problem. By combining predictive analytics with real-time monitoring, we aim to deliver a solution that offers accurate flood warnings and actionable insights. The system integrates cutting-edge algorithms and APIs for efficient deployment and accessibility, ensuring reliable forecasts to aid disaster management efforts.
            
            Advantages
            Provides early flood warnings, minimizing human and economic losses.
            Enables proactive measures by authorities and citizens.
            Combines historical and real-time data for accurate predictions.
            Enhances disaster preparedness and resource allocation.
            Utilizes cost-effective IoT sensors for real-time monitoring.
            Accessible via web and mobile platforms for broader reach.
            Scalable for integration with other geographic regions.
            Reduces reliance on manual monitoring systems.
            Promotes research and development in climate resilience.
            
            Limitations
            Dependency on accurate and complete historical data.
            High initial cost for IoT sensor installation.
            Requires regular maintenance of devices and systems.
            Limited accuracy in predicting extreme and rare flood events.
            Integration challenges with outdated infrastructure.
            
            Applications
            Disaster management and urban planning.
            Real-time flood monitoring and public alert systems.
            Insurance risk assessment and claims processing.
            Infrastructure design optimization.
            Educational tools for climate change awareness.
            Government policy and decision-making support.
            
            
        
        ```
use this information only to response correctly to the user question.
the reply should be smaller than 25 words strictly...

        Some current details: {get_current_time_and_location()}

        ML model predicated = "No Flood today and for upcomming 24 hrs"
        for Location = [churtgate to dadar to virar to palghar to dhanu]
        """
        
        # Add the user's new message to the chat history
        prompt = f"""systemPrompt: {systemPrompt}\nUserPrompt{chat_history}\nUser: {user_message}"""
        # print(f"prompt: \n{prompt}")

        # Call the Generative AI API
        try:
            response = geminimodel.generate_content(prompt)
            bot_response = response.text
        except Exception as e:
            bot_response = f"I'm sorry, but I couldn't process your request. {e}"

        # Save both user message and bot response to the database
        ChatData.objects.create(role="user",username=loggedUser, ChatText=user_message)
        ChatData.objects.create(role="bot",username=loggedUser, ChatText=f"{bot_response}")

        # Redirect to the chat page
        return redirect("chatbot")

    # Get all chats to display in the chat UI
    loggedUser = request.user.username  # Use the logged-in user's username

    # all_chats = ChatData.objects.all(username=loggedUser).order_by("timestamp")

    all_chats = ChatData.objects.filter(username=loggedUser).order_by("timestamp")

    
    return render(request, "floodsenseapp/chat.html", {"chats": all_chats})




# https://1be56469-efc1-4d75-8a1a-ad3133b3084a-00-2tx68ed5s69to.sisko.replit.dev/predict/?NodeName=Colaba&Latitude=18.91&Longitude=72.81&MonsoonIntensity=3&TopographyDrainage=1&RiverManagement=1&ClimateChange=6&Siltation=3&DrainageSystems=9&CoastalVulnerability=5&Watersheds=3&DeterioratingInfrastructure=4&WetlandLoss=2


# {"flood_probability": 45.11, "prediction_class": "No Flood Alert", "elapsed_time": 0.02}


# https://1be56469-efc1-4d75-8a1a-ad3133b3084a-00-2tx68ed5s69to.sisko.replit.dev/predict/?NodeName=Colaba&Latitude=18.91&Longitude=72.81&MonsoonIntensity=3&TopographyDrainage=36&RiverManagement=2&ClimateChange=6&Siltation=40&DrainageSystems=8&CoastalVulnerability=5&Watersheds=40&DeterioratingInfrastructure=9&WetlandLoss=2

# {"flood_probability": 55.27, "prediction_class": "Flood Alert", "elapsed_time": 0.05}

def predict(request):
    """
    Accepts query parameters with flood prediction factors, predicts flood probability, and returns a JSON response.
    """
    if request.method == "GET":
      try:
          start_time = time.time()
  
          # Extract parameters from the query string
          custom_json = {feature: float(request.GET.get(feature, 0)) for feature in feature_names}
          nodename = request.GET.get("NodeName", "Unknown Node")  
          latitude = request.GET.get("Latitude", "Unknown Node")  
          longitude = request.GET.get("Longitude", "Unknown Node")  
          # Default to 'Unknown Node' if not provided
  
          # Ensure input data matches the feature names
          custom_data = pd.DataFrame([custom_json], columns=feature_names)
          print(f"custom_data: {custom_data}")
  
          # Predict flood probability
          flood_probability = round((model.predict(custom_data)[0]) * 100, 2)
  
          # Determine prediction class based on flood probability
          if flood_probability >= 50.1:
              predicted_class = "Flood Alert"
              msgRecipients = "['prajusargar113@gmail.com']"

              address = get_location_address(latitude, longitude)
              print("Address:", address)

              message = f"Flood Alert: {nodename} at {address} has predicted flood for prbability of {flood_probability}%."
              sendEMailAlert("prajusargar113@gmail.com", "Flood Alert", message)
              add_alert_notify_data(nodename=nodename, msgRecipients=msgRecipients,
                                    msg=predicted_class)
          else:
              predicted_class  = "No Flood Alert"
  
          end_time = time.time()
          elapsed_time = round(end_time - start_time, 2)
          print(f"Elapsed time: {elapsed_time} seconds")
  
          # Call the add_sensor_data function to save the data
          add_sensor_data(
              nodename=nodename,
              latitude = str(latitude),
              longitude= str(longitude),
              monsoonintensity=str(custom_json.get("MonsoonIntensity", "")),
              topographydrainage=str(custom_json.get("TopographyDrainage", "")),
              rivermanagement=str(custom_json.get("RiverManagement", "")),
              climatechange=str(custom_json.get("ClimateChange", "")),
              siltation=str(custom_json.get("Siltation", "")),
              drainagesystems=str(custom_json.get("DrainageSystems", "")),
              coastalvulnerability=str(custom_json.get("CoastalVulnerability", "")),
              watersheds=str(custom_json.get("Watersheds", "")),
              deterioratinginfrastructure=str(custom_json.get("DeterioratingInfrastructure", "")),
              wetlandloss=str(custom_json.get("WetlandLoss", "")),
              predicttime=str(timezone.now()),
              predictionclass=predicted_class ,
              predictprobability=str(flood_probability)
          )
  
          # Return prediction result as JSON
          return JsonResponse({
              "flood_probability": flood_probability,
              "prediction_class": predicted_class ,
              "elapsed_time": elapsed_time
          })
  
      except Exception as e:
          # Handle and log any exceptions
          return JsonResponse({"error": str(e)}, status=500)
  
    # If not GET, render a placeholder page for testing
    return JsonResponse({"Message": "Only GET requests are allowed."})


def add_sensor_data(nodename: str, latitude: str, longitude: str, monsoonintensity: str, topographydrainage: str, rivermanagement: str, climatechange: str, siltation: str, drainagesystems: str, coastalvulnerability: str, watersheds: str, deterioratinginfrastructure: str, wetlandloss: str, predicttime: str, predictionclass: str, predictprobability: str) -> bool:
    """
    Adds a new record to the SensorData table.
    
    Args:
    nodename (str): Name of the sensor node.
    monsoonintensity (str): Monsoon intensity value.
    topographydrainage (str): Topography drainage value.
    rivermanagement (str): River management value.
    climatechange (str): Climate change value.
    siltation (str): Siltation value.
    drainagesystems (str): Drainage systems value.
    coastalvulnerability (str): Coastal vulnerability value.
    watersheds (str): Watersheds value.
    deterioratinginfrastructure (str): Deteriorating infrastructure value.
    wetlandloss (str): Wetland loss value.
    predicttime (str): Prediction time.
    predictionclass (str): Prediction class.
    predictprobability (str): Prediction probability.
    
    Returns:
    bool: True if data was added successfully, False otherwise.
    """
    try:
        # Create a new instance of SensorData
        sensor_data = SensorData(
        nodename=nodename,
        latitude=latitude,
        longitude=longitude,
        monsoonintensity=monsoonintensity,
        topographydrainage=topographydrainage,
        rivermanagement=rivermanagement,
        climatechange=climatechange,
        siltation=siltation,
        drainagesystems=drainagesystems,
        coastalvulnerability=coastalvulnerability,
        watersheds=watersheds,
        deterioratinginfrastructure=deterioratinginfrastructure,
        wetlandloss=wetlandloss,
        predicttime=predicttime,
        predictionclass=predictionclass,
        predictprobability=predictprobability,
        timestamp=timezone.now()  # Sets the timestamp to current time
        )
        
        # Save the instance to the database
        sensor_data.save()
        return True  # Indicate success
    
    except Exception as e:
        print(f"Error saving SensorData: {e}")
        return False  # Indicate failure



def add_alert_notify_data(nodename: str, msgRecipients: str, msg: str) -> bool:
    """
    Adds a new record to the AlertNotifyData table.
  
    Args:
    nodename (str): Name of the sensor node or location.
    msgRecipients (str): Recipients of the notification message.
    msg (str): The notification message content.
  
    Returns:
    bool: True if data was added successfully, False otherwise.
    """
    try:
        # Create a new instance of AlertNotifyData
        alert_notify_data = AlertNotifyData(
            nodename=nodename,
            msgRecipients=msgRecipients,
            msg=msg,
            timestamp=timezone.now()  # Sets the timestamp to current time
        )
  
        # Save the instance to the database
        alert_notify_data.save()
        return True  # Indicate success
  
    except Exception as e:
        print(f"Error saving AlertNotifyData: {e}")
        return False  # Indicate failure







def imgupload(request):
    """
    Handle image upload and save the image as Base64 text in the database.
    """
    if request.method == "POST" and request.FILES["image"]:
        uploaded_file = request.FILES["image"]

        # Convert image to Base64
        image = Image.open(uploaded_file)
        buffered = io.BytesIO()
        image.save(buffered, format="PNG")
        img_base64 = base64.b64encode(buffered.getvalue()).decode("utf-8")

        # Save the Base64 encoded image in the database
        ImgData.objects.create(
                nodename=request.POST.get("nodename", "Unknown Node"),
                imgBase64Text=img_base64
        )

        return redirect("gallery")  # Redirect to gallery view

    return render(request, "heartsense/imgUpload.html")













# Functions


def sendEMailAlert(emailAddress, subject, message):

    # Directly set the email parameters
    # address = "testemail@gmail.com"  # Replace with the recipient's email address
    # subject = "Welcome to Django Email Service"
    # message = "This is an automated email sent during a GET request."

    try:
        send_mail(subject, message, settings.EMAIL_HOST_USER, [emailAddress])
        return "Email sending is done"
    except Exception as e:
        errorMsg = f"Error sending email: {e}"
        print(errorMsg)
        return errorMsg


import requests

def get_location_address(latitude: float, longitude: float) -> str:
    """
    Fetches the address of a given latitude and longitude using OpenStreetMap Nominatim API.

    Args:
        latitude (float): Latitude of the location.
        longitude (float): Longitude of the location.

    Returns:
        str: The address of the location or an error message if not found.
    """
    try:
        # Nominatim API endpoint
        url = "https://nominatim.openstreetmap.org/reverse"
        params = {
            'lat': latitude,
            'lon': longitude,
            'format': 'json',
        }

        # User-Agent header (required by Nominatim)
        headers = {
            'User-Agent': 'MyPythonApp/1.0 (your_email@example.com)'  # Replace with your app name and email
        }

        # Make a GET request to the Nominatim API
        response = requests.get(url, params=params, headers=headers, timeout=10)
        response.raise_for_status()  # Raise an error for bad status codes

        # Parse the response JSON
        data = response.json()

        # Extract the address from the response
        if 'address' in data:
            return data.get('display_name', 'Address not available')
        else:
            return "Address not found for the given coordinates."

    except requests.exceptions.RequestException as e:
        return f"Error fetching address: {e}"

# Example usage
# latitude = 19.0163
# longitude = 72.8291
# address = get_location_address(latitude, longitude)
# print("Address:", address)




def user_register(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        email = request.POST['email']

        # Check if the username is unique
        if not User.objects.filter(username=username).exists():
            # Create a new user
            user = User.objects.create_user(username=username,
                                            password=password,
                                            email=email)
            return redirect('user_login')  # Redirect to your login view
        else:
            error_message = 'Username already exists'
    else:
        error_message = None

    return render(request, 'floodsenseapp/register.html',
                  {'error_message': error_message})


def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')  # Redirect to your dashboard view
        else:
            error_message = 'Invalid username or password'
    else:
        error_message = None

    return render(request, 'floodsenseapp/login.html',
                  {'error_message': error_message})


def user_logout(request):
    logout(request)
    return redirect('user_login')  # Redirect to your login view




