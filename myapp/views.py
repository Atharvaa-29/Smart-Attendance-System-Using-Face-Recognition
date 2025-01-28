from datetime import datetime
import json
import os
import uuid
import zipfile
from django.shortcuts import get_object_or_404, redirect, render
from django.http import HttpResponse, JsonResponse
from django.conf import settings
from django.contrib.auth import login as auth_login, logout as auth_logout
import openpyxl
from myapp.models import Course, Faculty, Student

# Define the uploads folder paths
uploads_folder = os.path.join(settings.BASE_DIR, "static", "peeps", "temp", "uploads")
uploads_folder_extract = os.path.join(settings.BASE_DIR, "static", "peeps", "uploads")

# Ensure the uploads folder exists
if not os.path.exists(uploads_folder):
    os.makedirs(uploads_folder)



def main(request):
    return render(request ,"main.html")


# User login
def login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        is_faculty = request.POST.get("isfaculty")
        print(username)
        print(password)
        if is_faculty:  # Faculty login
            try:
                faculty = Faculty.objects.get(name=username)
                if faculty.check_password(password):
                    # auth_login(request, faculty)  # Log in the faculty
                    token = str(uuid.uuid4())  # Generate a unique token
                    # Save the token in the session or database as needed
                    request.session["token"] = token  # Store token in session
                    return JsonResponse(
                        {"token": token, "redirect": f"/faculty/{username}/"}
                    )
                else:
                    return JsonResponse(
                        {"error": "Invalid Username or Password"}, status=401
                    )
            except Faculty.DoesNotExist:
                return JsonResponse(
                    {"error": "Invalid Username or Password"}, status=401
                )
        else:  # Student login
            try:
                student = Student.objects.get(name=username)
                if (
                    student.password == password
                ):  # Verify password (you should hash this!)
                    # auth_login(request, student)  # Log in the student
                    token = str(uuid.uuid4())  # Generate a unique token
                    request.session["token"] = token  # Store token in session
                    return JsonResponse(
                        {"token": token, "redirect": f"/student/{username}/"}
                    )
                else:
                    return JsonResponse(
                        {"error": "Invalid Username or Password"}, status=401
                    )
            except Student.DoesNotExist:
                return JsonResponse(
                    {"error": "Invalid Username or Password"}, status=401
                )

    return render(request, "login.html")


# User signup
def signup(request):
    if request.method == "POST":
        roll_no = request.POST.get("roll_no")
        name = request.POST.get("name")
        password = request.POST.get("pass2")
        zip_file = request.FILES.get(
            "file"
        )  # Correct the key to match the uploaded ZIP file

        # Create student instance and save it
        student = Student(roll_no=roll_no, name=name, password=password)
        student.save()  # Save the student user

        # Define the directory to save the images
        uploads_folder = os.path.join(
            settings.BASE_DIR, "static", "peeps", "uploads", name
        )

        zip_folder = os.path.join(
            settings.BASE_DIR, "static", "peeps", "temp", "uploads"
        )

        # Ensure the directory exists
        os.makedirs(uploads_folder, exist_ok=True)
        print("Upload folder created at:", uploads_folder)

        # Save and extract the zip file
        if zip_file:
            zip_path = os.path.join(zip_folder, "images.zip")
            with open(zip_path, "wb+") as destination:
                for chunk in zip_file.chunks():
                    destination.write(chunk)

            # Check if the ZIP file was saved successfully
            if os.path.exists(zip_path):
                print("ZIP file saved at:", zip_path)
            else:
                print("Failed to save ZIP file.")

            # Extract images from the zip file
            try:
                with zipfile.ZipFile(zip_path, "r") as zip_ref:
                    zip_ref.extractall(uploads_folder)  # Extract to the uploads folder
                    print("ZIP file extracted successfully.")
            except Exception as e:
                print("Error extracting ZIP file:", e)

            # List files in the uploads folder to see what has been extracted
            extracted_files = os.listdir(uploads_folder)
            print("Extracted files:", extracted_files)

        # Update manifest.json
        manifest_path = os.path.join(
            settings.BASE_DIR, "static", "peeps", "manifest.json"
        )

        # Read the current manifest data
        if os.path.exists(manifest_path):
            with open(manifest_path, "r") as manifest_file:
                try:
                    manifest_data = json.load(manifest_file)
                    # Ensure the 'labels' key exists and is a list
                    if "labels" not in manifest_data or not isinstance(
                        manifest_data["labels"], list
                    ):
                        manifest_data["labels"] = (
                            []
                        )  # Initialize as an empty list if it doesn't exist
                except json.JSONDecodeError:
                    manifest_data = {
                        "labels": []
                    }  # Initialize as a new structure if JSON is invalid
        else:
            manifest_data = {
                "labels": []
            }  # Initialize as a new structure if the file doesn't exist

        # Update the manifest with the new student info
        manifest_data["labels"].append(
            [name, 20]
        )  # Add the student's name and a fixed value (20)

        # Write the updated manifest data back to the file
        with open(manifest_path, "w") as manifest_file:
            json.dump(
                manifest_data, manifest_file, indent=4
            )  # Use indent for better readability

        os.remove(os.path.join(zip_folder, "images.zip"))

        return redirect("login")  # Redirect to login after signup

    return render(request, "student_signup.html")


# Student Dashboard
def student_dashboard(request, name):
    # # Check if the token is present (assuming it's sent as a header)
    # token = request.META.get("HTTP_AUTHORIZATION")

    # if not token:
    #     # Redirect to login or handle the absence of token
    #     return redirect("/login/")  # Change this URL to your actual login URL

    # Get the student by name
    student = get_object_or_404(Student, name=name)

    if request.method == "POST":
        # Handle profile update
        if "name" in request.POST:
            student.name = request.POST.get("name")
            student.save()
            return redirect("student_dashboard", name=student.name)

        # Handle course enrollment
        if "course" in request.POST:
            course_id = request.POST.get("course")
            course = get_object_or_404(Course, id=course_id)
            student.courses.add(course)  # Enroll in the course
            return redirect("student_dashboard", name=student.name)

        # Handle course unenrollment
        if "unenroll_course" in request.POST:
            course_id = request.POST.get("unenroll_course")
            course = get_object_or_404(Course, id=course_id)
            student.courses.remove(course)  # Unenroll from the course
            return redirect("student_dashboard", name=student.name)

    # Fetch available courses for the dropdown
    courses = Course.objects.all()
    enrolled_courses = student.courses.all()
    return render(
        request,
        "student_dashboard.html",
        {"student": student, "courses": courses, "enrolled_courses": enrolled_courses},
    )


def upload_image(request):
    if request.method == "POST" and request.FILES:
        zip_file = request.FILES.get("image")  # Get the uploaded ZIP file
        name = request.POST.get("name")  # Get the uploaded ZIP file
        if zip_file:
            # Define folders for uploads
            zip_folder = os.path.join(
                settings.BASE_DIR, "static", "peeps", "temp", "uploads"
            )
            uploads_folder = os.path.join(
                settings.BASE_DIR, "static", "peeps", "uploads", name
            )
            # Ensure folders exist
            os.makedirs(zip_folder, exist_ok=True)
            os.makedirs(uploads_folder, exist_ok=True)

            # Save the uploaded ZIP file
            zip_path = os.path.join(zip_folder, "images.zip")
            with open(zip_path, "wb+") as destination:
                for chunk in zip_file.chunks():
                    destination.write(chunk)

            # Check if the ZIP file was saved successfully
            if os.path.exists(zip_path):
                print("ZIP file saved at:", zip_path)
            else:
                return JsonResponse({"message": "Failed to save ZIP file."}, status=400)

            # Extract images from the ZIP file
            try:
                with zipfile.ZipFile(zip_path, "r") as zip_ref:
                    zip_ref.extractall(uploads_folder)  # Extract to the uploads folder
                    print("ZIP file extracted successfully.")
            except Exception as e:
                print("Error extracting ZIP file:", e)
                return JsonResponse(
                    {"message": "Error extracting ZIP file."}, status=400
                )

            # List files in the uploads folder to see what has been extracted
            extracted_files = os.listdir(uploads_folder)
            print("Extracted files:", extracted_files)

            # Update manifest.json
            manifest_path = os.path.join(
                settings.BASE_DIR, "static", "peeps", "manifest.json"
            )

            # Read the current manifest data
            if os.path.exists(manifest_path):
                with open(manifest_path, "r") as manifest_file:
                    try:
                        manifest_data = json.load(manifest_file)
                        # Ensure the 'labels' key exists and is a list
                        if "labels" not in manifest_data or not isinstance(
                            manifest_data["labels"], list
                        ):
                            manifest_data["labels"] = (
                                []
                            )  # Initialize as an empty list if it doesn't exist
                    except json.JSONDecodeError:
                        manifest_data = {
                            "labels": []
                        }  # Initialize as a new structure if JSON is invalid
            else:
                manifest_data = {
                    "labels": []
                }  # Initialize as a new structure if the file doesn't exist

            # Update the manifest with the new student info (use appropriate data)
            name = name  # Replace with the actual student's name as needed
            manifest_data["labels"].append(
                [name, 20]
            )  # Add the student's name and a fixed value (20)

            # Write the updated manifest data back to the file
            with open(manifest_path, "w") as manifest_file:
                json.dump(
                    manifest_data, manifest_file, indent=4
                )  # Use indent for better readability

            # Clean up: remove the ZIP file
            os.remove(zip_path)

            return JsonResponse(
                {
                    "message": "Images uploaded and processed successfully.",
                    "extracted_files": extracted_files,
                }
            )

    return JsonResponse({"message": "Invalid request."}, status=400)


# Faculty signup
def faculty_signup(request):
    if request.method == "POST":
        username = request.POST.get("name")
        password = request.POST.get("pass2")

        faculty = Faculty.objects.create(name=username)
        faculty.set_password(password)  # Hash the password
        faculty.save()  # Save the faculty user
        return redirect("faculty_login")  # Redirect to faculty login after signup

    return render(request, "faculty_signup.html")


def faculty_dashboard(request, faculty_name):
    # Get the faculty by their name
    faculty = get_object_or_404(Faculty, name=faculty_name)

    # Get all the courses this faculty teaches
    # You can adjust the logic here to filter courses based on the faculty if needed.
    courses = (
        Course.objects.all()
    )  # Adjust logic to filter based on faculty if applicable

    context = {
        "faculty": faculty,
        "courses": courses,
    }
    return render(request, "faculty_dashboard.html", context)


def take_attendance(request, course_id):
    # Get the course by ID
    course = get_object_or_404(Course, id=course_id)

    # Get all students enrolled in the course
    students = course.students.all()

    if request.method == "POST":
        # Get the attendance data from the form
        attendance_data = request.POST.getlist("attendance")

        print(students)
        print(attendance_data)

        # Create an Excel file with attendance data
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = f"Attendance for {course.course}"

        # Add headers
        ws.append(["Roll No", "Name", "Present"])

        # Initialize counts
        total_present = 0
        total_absent = 0

        # Add student data to the Excel sheet
        for student in students:
            is_present = "Yes" if str(student.name) in attendance_data[0] else "No"
            ws.append([student.roll_no, student.name, is_present])

            # Update counts
            if is_present == "Yes":
                total_present += 1
            else:
                total_absent += 1

        # Add totals to the Excel sheet
        ws.append([])
        ws.append(["Total Present", total_present])
        ws.append(["Total Absent", total_absent])
        ws.append(["Date", datetime.now().strftime("%Y-%m-%d")])  # Add current date

        # Prepare the file to be downloaded
        response = HttpResponse(
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        response["Content-Disposition"] = (
            f"attachment; filename=attendance_{course.course}.xlsx"
        )

        # Save the workbook to the response
        wb.save(response)

        return response

    context = {
        "course": course,
        "students": students,
    }
    return render(request, "take_attendance.html", context)


# Faculty login
def faculty_login(request):
    return redirect("login")  # Redirect faculty login to the same login page


# Logout function
def logout(request):
    auth_logout(request)  # Log out the user
    return redirect("login")  # Redirect to home page
