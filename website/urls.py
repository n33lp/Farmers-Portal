from django.contrib import admin
from django.urls import path, include
from . import views
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from website.views import login_view,check_reference_id
from django.contrib.auth import views as auth_views



urlpatterns = [
    path('',views.home,name='home'),
    path('employee',views.employee,name='employee'),
    path('login/', login_view, name='login'),
    path('upload/', views.upload_view, name='upload'),
    path('check_reference_id/', check_reference_id, name='check_reference_id'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),

]