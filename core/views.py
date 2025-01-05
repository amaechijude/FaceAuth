import json
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.core.files.storage import default_storage

from core.models import User
from .forms import RegisterForm
import face_recognition
# Create your views here.

def generate_picture_encodings(picture_path: str) -> tuple:
    img = face_recognition.load_image_file(picture_path) # loads the image
    img_encodings = face_recognition.face_encodings(img)

    face_found = True if len(img_encodings) > 0 else False
    return (face_found, img_encodings)

def compare_picture_encodings(saved_picture_encoding: list, uploaded_picture_encoding: list) -> bool:
    compare_result = face_recognition.compare_faces([saved_picture_encoding], uploaded_picture_encoding[0])

    return True if compare_result[0] else False


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
    if not request.method == 'POST':
        return HttpResponse("Invalid method")
    
    email = request.POST.get('email')
    profile_picture = request.FILES.get('profile_picture')

    if not email or not profile_picture:
        return HttpResponse("Email and Profile picture is required")
    
    # Try finding user
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
    match_profile_picture: bool = compare_picture_encodings(list(user.profile_picture_encodings), img_encoding)
    if not match_profile_picture:
        return HttpResponse("Profile picture was not Match. Contact the admin")
    
    login(request, user)
    return redirect('index_page')

@login_required(login_url='login_user')
def index_page(request):
    return render(request, 'index.html')
