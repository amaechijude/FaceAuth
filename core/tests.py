import os
from django.test import TestCase, Client
from django.core.files import File
from .models import User
from FaceAuth.settings import BASE_DIR
from .views import generate_picture_encodings, compare_picture_encodings#, index_page, register_user, login_user



img_path = os.path.join(BASE_DIR, 'media', 'test.jpg')
primary_img = os.path.join(BASE_DIR, 'media', 'primary.jpg')
# Test User Model creation
class UserTestCase(TestCase):
    def setUp(self):
        self.face_found, self.img_encodings = generate_picture_encodings(img_path)
        self.user = User.objects.create(
            email = "user@email.com",
            password = "password", full_name = "User Name", 
            profile_picture_encodings = self.img_encodings
            )
        with open(img_path, 'rb') as img:
            img_file = File(img)
            self.user.profile_picture = img_file
        
    def test_user_creation(self):
        self.assertEqual(self.user.email, "user@email.com")
        self.assertEqual(self.user.password, "password")
        self.assertEqual(self.user.full_name, "User Name")
        self.assertEqual(self.user.profile_picture_encodings, self.img_encodings)
        self.assertTrue(self.face_found)
        self.assertTrue(self.user.profile_picture)


# Test the views and functions
class TestCompareEncoding(TestCase):
    def setUp(self):
        self.face_found, self.img_encodings = generate_picture_encodings(img_path)
        self.second_face_found, self.second_img_encodings = generate_picture_encodings(primary_img)
        #compare
        self.compare = compare_picture_encodings(self.img_encodings, self.second_img_encodings)

    def test_comparism(self):
        self.assertTrue(self.compare)
        self.assertTrue(self.face_found)
        self.assertTrue(self.second_face_found)


class TestIndexView(TestCase):
    def setup(self):
        self.client = Client()
    
    def test_index_page(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 302) # 300 for redirect to login page
        self.assertTemplateUsed('index.html')

class TestRegisterView(TestCase):
    def setup(self):
        self.face_found, self.img_encodings = generate_picture_encodings(img_path)
        self.client = Client()
    
    def test_register_page(self):
        response = self.client.get('/user/register')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('register.html')

    def test_register_user(self):
        face_found, img_encodings = generate_picture_encodings(img_path)
        response = self.client.post('/user/register', {
            'email': "user@email.com",
            'password':"password", 'full_name': "User Name",
            'profile_picture_encodings': img_encodings
        })
        self.assertEqual(response.status_code, 200)
        self.assertTrue(face_found)
