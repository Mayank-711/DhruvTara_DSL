# views.py
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from .models import UserProfile


def landingpage(request):
    return render(request, 'authapp/landingpage.html')



def signup_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        phone_number = request.POST.get('phone_number')
        date_of_birth = request.POST.get('date_of_birth')
        school = request.POST.get('school')
        grade = request.POST.get('grade')
        

        if password1 != password2:
            messages.error(request, "Passwords don't match")
            return redirect('signup')
        

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists")
            return redirect('signup')
        

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered")
            return redirect('signup')
        

        try:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password1,
                first_name=first_name,
                last_name=last_name
            )
            

            UserProfile.objects.create(
                user=user,
                phone_number=phone_number,
                date_of_birth=date_of_birth,
                school=school,
                grade=grade
            )
            
            messages.success(request, 'Account created successfully!')
            return redirect('login')
            
        except Exception as e:
            messages.error(request, f'Error creating account: {str(e)}')
            return redirect('signup')
    
    return render(request, 'authapp/signup.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password.')
    
    return render(request, 'authapp/login.html')

@login_required
def logout_view(request):
    logout(request)
    return redirect('landingpage')