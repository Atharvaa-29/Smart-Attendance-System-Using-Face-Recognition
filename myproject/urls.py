from django.contrib import admin
from django.urls import path, re_path
from django.conf import settings
from django.conf.urls.static import static
from myapp import views  # Replace 'myapp' with your app name

urlpatterns = [

    path("admin/", admin.site.urls),
    path("", views.main ,name ="main"),
    path("login/", views.login, name="login"),  # User login
    path("signup/", views.signup, name="signup"),  # User signup
    
    path("facultylogin/", views.faculty_login, name="faculty_login"),  # Faculty login
    path(
        "facultysignup/", views.faculty_signup, name="faculty_signup"
    ),  # Faculty signup
    path(
        "student/<str:name>/", views.student_dashboard, name="student_dashboard"
    ),  # Student dashboard
    path("upload_image/", views.upload_image, name="upload_image"),  # Add this line
    path(
        "faculty/<str:faculty_name>/", views.faculty_dashboard, name="faculty_dashboard"
    ),
    path("course/<int:course_id>/", views.take_attendance, name="take_attendance"),
    path("logout/", views.logout, name="logout"),  # Logout
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
