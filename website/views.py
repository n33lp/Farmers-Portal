import secrets
import string
import os
import random
import secrets
import pandas as pd
import gmplot
import numpy as np
import re
import vonage
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.http import HttpResponse
from django.conf import settings
from .models import UploadedData
from django.conf import settings
from django.db.models import Q
from django.http import JsonResponse
from django.core.files.storage import FileSystemStorage
from .forms import YourForm
from django.http import HttpResponseBadRequest
from django import forms
from FungiLink import settings
from django.core.mail import send_mail
from django.core.mail import EmailMessage
from django.contrib.auth.decorators import login_required



# Create your views here.
def home(request):
    return render(request, "website/index.html")

def employee(request):
    return render(request, "website/employee.html")

# Generate a unique reference key
def generate_reference_key_view():
    alphanumeric = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphanumeric) for _ in range(8))

# Save the uploaded CSV file with a unique name
def save_csv_file(csv_file, reference_key):
    original_file_name, file_extension = os.path.splitext(csv_file.name)
    new_file_name = f'{reference_key}{file_extension}'
    file_path = os.path.join(settings.BASE_DIR, 'csv_files', new_file_name)

    with open(file_path, 'wb+') as destination:
        for chunk in csv_file.chunks():
            destination.write(chunk)

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('upload')
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'website/employee.html')

def generate_reference_id():
    length = 8
    while True:
        reference_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))
        if not UploadedData.objects.filter(reference_id=reference_id).exists():
            return reference_id

def check_reference_id(request):
    if request.method == 'POST':
        reference_id = request.POST.get('reference-id')
        print(reference_id)
        # Perform the check to see if the ID exists in your data
        if UploadedData.objects.filter(reference_id=reference_id).exists():
            # Redirect to the results page
            data = UploadedData.objects.get(reference_id=reference_id)
            template_name = f'heatmaps/{reference_id}.html'

            with open(f'templates/heatmaps/{reference_id}.html', 'r') as file:
                html_code = file.read()
            script_tags = re.findall(r'<script.*?>.*?<\/script>', html_code, re.DOTALL)
            
            context = {
                'name': f"{data.first_name} {data.last_name}" if data else '',
                'employee': data.ename if data else '',
                'reference_id' :data.reference_id,
                'script': script_tags,
                
            }
            return render(request, "website/results.html",context)
        else:
            # Handle the case when the ID doesn't exist
            return render(request, 'website/index.html')

    return render(request, 'website/index.html')

@login_required(login_url='employee')
def upload_view(request):
    form = YourForm()  # Define the form outside the 'if' statement
    
    if request.method == 'POST':
        form = YourForm(request.POST, request.FILES)
        if form.is_valid():
            csv_file = request.FILES.get('csv_file')
            if csv_file:
                fs = FileSystemStorage(location='csv_files/')
                # Generate a unique filename using reference_id
                x=generate_reference_id()
                filename = f"{x}.csv"
                uploaded_file_path = fs.save(filename, csv_file)
                # Get the complete file path
                file_path = os.path.join('csv_files', uploaded_file_path)
                heat(file_path)  # Pass the complete file path to heat function
                # Save the relevant data to the UploadedData model
                reference_id = x
                first_name = form.cleaned_data.get('first_name')
                last_name = form.cleaned_data.get('last_name')
                email = form.cleaned_data.get('email')
                phone_number = form.cleaned_data.get('phone_number')
                ename = request.user.first_name
                uploaded_data = UploadedData(
                    reference_id=reference_id,
                    first_name=first_name,
                    last_name=last_name,
                    email=email,
                    phone_number=phone_number,
                    ename=ename
                )
                uploaded_data.save()
                messages.success(request, 'Saved')
                send_confirmation_email_customer(email,reference_id,first_name,ename)
                #employee_email='ualbertaigem2023@gmail.com'
                employee_email = request.user.email
                customer_name = first_name+' '+last_name
                user_email=employee_email
                employee_name=ename
                send_confirmation_email_employee(user_email,reference_id,customer_name,employee_name)
                send_sms(phone_number,first_name,employee_name,reference_id)

            else:
                messages.success(request,'No CSV file uploaded')
        else:
            messages.success(request, 'Error saving entry, please fill in the form correctly')
            if form.errors:
                print(form.errors)

    return render(request, 'website/upload.html', {'form': form})

def heat(file_path):
    file_name = os.path.basename(file_path)
    file_name_without_ext = os.path.splitext(file_name)[0]
    html_file_name = f"{file_name_without_ext}.html"
    gmap_api_key=""
    # Read the CSV file
    data = pd.read_csv(file_path)
    # Read the CSV file
    # Extract the latitude and longitude columns from the DataFrame
    latitude = data['Latitude']
    longitude = data['Longitude']

    # Calculate the frequency of each unique coordinate
    coordinates = np.column_stack((latitude, longitude))
    unique_coordinates, counts = np.unique(coordinates, axis=0, return_counts=True)

    # Check if all counts are the same
    if np.ptp(counts) == 0:
        normalized_counts = np.full_like(counts, 0)  # Set all counts to 0 or 1 as per your preference
    else:
        # Normalize the counts to the range [0, 1]
        normalized_counts = (counts - min(counts)) / (max(counts) - min(counts))

    # Calculate the center point of the coordinates
    center_latitude = np.mean(latitude)
    center_longitude = np.mean(longitude)

    # Specify the zoom level for the map
    zoom = 16

    # Create a gmplot object with the center coordinates, zoom level, and map type
    gmap = gmplot.GoogleMapPlotter(center_latitude, center_longitude, zoom, apikey=gmap_api_key, map_type='satellite')

    # Generate the heatmap using the normalized counts
    gmap.heatmap(unique_coordinates[:, 0], unique_coordinates[:, 1], weights=normalized_counts, radius=25)
        # Save the HTML file with the same name as the CSV file in 'templates/heatmaps'
    fs = FileSystemStorage(location='templates/heatmaps/')
    html_content = gmap.get()
    file_path = fs.path(html_file_name)  # name of file
    with open(file_path, 'w') as file:
        file.write(html_content)
    
def send_confirmation_email_customer(user_email,reference_id,customer_name,employee_name):
    subject = 'Your Reference ID for FungiLink'
    email_template = """
    Hey {customer_name},
    
    Thank you for using our services! We would like to provide you with the reference ID for your recent request. This reference ID will help you track the progress and access the results of your scan.
    
    Reference ID: {reference_id}
    
    To access the scan results and other details, please visit our website and enter your reference ID on the designated page. If you have any questions or need further assistance, feel free to reach out to our support team.
    
    We appreciate your trust in our services and look forward to serving you again in the future.
    
    Best regards,
    {your_name}
    Team UAlberta
    """
    formatted_email = email_template.format(
        customer_name=customer_name,
        reference_id=reference_id,
        your_name=employee_name,
        )


    email = EmailMessage(subject, formatted_email, to=[user_email])
    email.send()

def send_confirmation_email_employee(user_email, reference_id, customer_name, employee_name):
    subject = 'Reference ID for {customer_name}'

    subject_email = subject.format(customer_name=customer_name)

    email_template = """
    Hi {employee_name},

    Great Job with the scan for {customer_name}. Please refer below for their Reference ID.

    Reference ID: {reference_id}

    If you have any questions or need further assistance, feel free to reach out to the IT team.

    We appreciate your hard work in making this service great for our customers.

    Best regards,
    Neel Patel
    Director of Technology
    Team UAlberta
    """

    formatted_email = email_template.format(
        employee_name=employee_name,
        customer_name=customer_name,
        reference_id=reference_id,
    )
    email = EmailMessage(subject_email, formatted_email, to=[user_email])
    email.send()

def send_sms(customer_num,customer_name,employee_name,reference_id):
    customer_num = '1'+''.join(customer_num.split('-'))
    message="""
    Hi {customer_name} here is your reference ID for the scan that was taken by {employee_name}.
    Reference ID: {reference_id}
    """
    message=message.format(
        customer_name=customer_name,
        employee_name=employee_name,
        reference_id=reference_id,
    )
    client = vonage.Client(key="", secret="")
    sms = vonage.Sms(client)
    responseData = sms.send_message(
        {
            "from": "15815336608",
            "to": customer_num,
            "text": message,
        }
    )

    if responseData["messages"][0]["status"] == "0":
        print("Message sent successfully.")
    else:
        print(f"Message failed with error: {responseData['messages'][0]['error-text']}")