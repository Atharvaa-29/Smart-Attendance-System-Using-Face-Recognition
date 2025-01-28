from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.contrib import admin

from myapp.models import Course, Degree, Faculty, Student


# Admin Configuration
class StudentAdmin(admin.ModelAdmin):
    list_display = ("roll_no", "name")  
    search_fields = ("name",) 
    ordering = ("roll_no",)  


class FacultyAdmin(admin.ModelAdmin):
    list_display = ("name",)  # Use the correct field here
    search_fields = ("name",)  # Searchable fields in the admin interface
    ordering = ("name",)  # Default ordering


class DegreeAdmin(admin.ModelAdmin):
    list_display = ("degree", "years", "branches")  # Fields to display
    search_fields = ("degree",)  # Searchable fields


class CourseAdmin(admin.ModelAdmin):
    list_display = ("course", "year", "branch", "degree")  # Fields to display
    search_fields = ("course", "branch", "degree__degree")  # Searchable fields


# Register your models
admin.site.register(Student, StudentAdmin)
admin.site.register(Faculty, FacultyAdmin)
admin.site.register(Degree, DegreeAdmin)
admin.site.register(Course, CourseAdmin)
