import json
import pprint
from FaceAuth.settings import GEMINI_API_KEY
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout
from django.core.files.storage import default_storage
from django.views.decorators.csrf import csrf_exempt
from google import genai
# from google.genai import types
import numpy as np

from core.models import User
from .forms import RegisterForm


import face_recognition

def generate_picture_encodings(picture_path: str) -> tuple:
    img = face_recognition.load_image_file(picture_path) # loads the image
    img_encodings = face_recognition.face_encodings(img)
    np_array = np.array(img_encodings)
    face_found = True if len(img_encodings) > 0 else False
    return (face_found, np_array.tolist())

def compare_picture_encodings(saved_picture_encoding: json, uploaded_picture_encoding: json) -> bool:
    data_1 = np.array(saved_picture_encoding)
    data_2 = np.array(uploaded_picture_encoding)
    compare_result = face_recognition.compare_faces(data_1, data_2[0])
    try:
        compare_output = compare_result[0]
    except IndexError:
        return False
    return True if compare_output else False


def register_user(request):
    if request.method == 'GET':
        form = RegisterForm()
        return render(request, 'register.html', {"form": form})
    
    if request.method == 'POST':
        form = RegisterForm(request.POST, request.FILES)
        if not form.is_valid():
            data = json.dumps(form.errors, indent=4)
            return HttpResponse(data)
        
        user = form.save(commit=False)
        profile_picture = form.cleaned_data['profile_picture']

        # temporary save the image
        temp_image_path = default_storage.save("profile_picture", profile_picture)
        face_found, img_encodings = generate_picture_encodings(default_storage.path(temp_image_path))

        if not face_found:
            default_storage.delete(temp_image_path)
            return HttpResponse("Unable to detect face in the image")

        user.profile_picture_encodings = img_encodings
        user.save()
        default_storage.delete(temp_image_path)
        return redirect('login_user')


def login_user(request):
    if request.method == 'GET':
        return render(request, 'login.html')
    if request.method == 'POST':
        email = request.POST.get('email')
        profile_picture = request.FILES.get('profile_picture')
        if not email or not profile_picture:
            return HttpResponse("Email and Profile picture is required")
        
        # Try finding user  ``
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return HttpResponse(f"User with the email: {email} does not exist or is no longer active")
        
        ## try process uploaded image
        try:
            face_found, img_encoding = generate_picture_encodings(profile_picture)
            if not face_found:
                return HttpResponse("No face Detected")
        except Exception as e:
            data = {"message": "Unable to process image", "Error": e}
            return HttpResponse(json.dumps(data, indent=4))
        
        # compare
        match_profile_picture: bool = compare_picture_encodings(user.profile_picture_encodings, img_encoding)
        if not match_profile_picture:
            return HttpResponse("Profile picture was not Match. Contact the admin")
        
        ## Loging an redirect the user
        login(request, user)
        return redirect('index_page')

@login_required(login_url='login_user')
def index_page(request):
    return render(request, 'index.html')

def logout_user(request):
    logout(request)
    return redirect('login_user')


@csrf_exempt
def get_vacation_recomendation(request):
    if not request.method == 'POST':
        return HttpResponse("Method not supported")

    starting_point = request.POST.get('starting_point')
    destination = request.POST.get('destination')
    travel_dates = request.POST.get("travel_dates")
    budget = request.POST.get('budget')
    group_size = request.POST.get("group_size")
    activities = request.POST.get("activities")
    accommodation = request.POST.get("accommodation")
    special_requirements = request.POST.get("special_requirements")

    prompt = f"""
        I am planning a vacation and need personalized recommendations based on the following details:

        0. **Staring Point** {starting_point}
        1. **Destination Preferences:** {destination}.  
        2. **Travel Dates:** {travel_dates}.  
        3. **Budget:** Approximately {budget}.  
        4. **Group Size and Type:** {group_size}.  
        5. **Activities:**  {activities}.  
        6. **Accommodation Preferences:** {accommodation}.
        7. **Special Requirements:** {special_requirements}.

        Based on this information, can you suggest a detailed vacation plan, including recommended destinations, activities, accommodations, and any additional travel tips?
    """
    client = genai.Client(api_key=GEMINI_API_KEY)
    try:
        response = client.models.generate_content(model='gemini-1.5-flash', contents=prompt)
        pprint.pprint(response.text)
    except Exception as e:
        pprint.pprint(e)
        return JsonResponse({
            "failed": "failed",
            "response": "Ai unable to generate recommendations. Try again later",
        })
    
    return JsonResponse({
        "success": "success",
        "response": response.text
    })
