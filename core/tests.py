import os
from django.test import TestCase
from django.core.files import File
from .models import User
from FaceAuth.settings import BASE_DIR
from .views import generate_picture_encodings, compare_picture_encodings, index_page, register_user, login_user



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
        self.face_found_second, self.img_encodings_second = generate_picture_encodings(primary_img)
        #compare
        self.compare = compare_picture_encodings(self.img_encodings, self.img_encodings_second)

    def test_comparism(self):
        self.assertTrue(self.compare)
        self.assertTrue(self.face_found)
        self.assertTrue(self.face_found_second)

# class TestIndexView(TestCase):
#     def setup(self):
#         pass
