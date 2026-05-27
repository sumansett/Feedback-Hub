from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.core.mail import send_mail
from django.conf import settings
from .models import OtpModel
import random
import re
from django.utils import timezone
from datetime import timedelta


def register(request):

    if request.method == 'POST':
        name = request.POST.get('username')
        email = request.POST.get('useremail')
        password = request.POST.get('password')

        # Password validation
        if len(password) < 8:
            messages.error(request, 'Password must be at least 8 characters long')
            return redirect('register')

        if not re.search(r'[A-Z]', password):
            messages.error(request, 'Password must contain at least one uppercase letter')
            return redirect('register')

        if not re.search(r'[a-z]', password):
            messages.error(request, 'Password must contain at least one lowercase letter')
            return redirect('register')

        if not re.search(r'[0-9]', password):
            messages.error(request, 'Password must contain at least one number')
            return redirect('register')

        if not re.search(r'[@$!%*?&]', password):
            messages.error(request, 'Password must contain at least one special character')
            return redirect('register')

        userAlreadyExist=User.objects.filter(username=name).exists()
        emalilAlreadyExist=User.objects.filter(email=email).exists()
        

        if userAlreadyExist:
            messages.error(request, 'Username or already exists')
            return redirect('register')
        if emalilAlreadyExist:
            messages.error(request, 'Email already exists')
            return redirect('register')
        newuser = User.objects.create_user(username=name, email=email, password=password)
        newuser.save()
        messages.success(request, 'Registration successful')
        return redirect('login')

    return render(request, 'register.html')


def Login(request):
    if request.method == 'POST':
        name = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=name, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, 'Login successful')

            next = request.GET.get('next')
            if next:
                return redirect(next)
            return redirect('home')
        
        else:
            messages.error(request, 'Invalid username or password')
            return redirect('login')

    return render(request, 'login.html')


def Logout(request):
    logout(request)
    messages.success(request, 'Logout successful')
    return redirect('login')

def ForgetPassword(request):

    # SEND OTP
    if request.method == 'POST' and 'send_otp' in request.POST:
        username_or_email = request.POST.get('username_or_email')

        if not username_or_email:
            messages.error(request, 'Please enter your username or email.')
            return redirect('forget-password')

        username_or_email = username_or_email.strip()

        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

        if re.match(email_regex, username_or_email):
            user = User.objects.filter(email=username_or_email).first()

            if user is None:
                messages.error(request, 'No account found with this email.')
                return redirect('forget-password')

        else:
            user = User.objects.filter(username=username_or_email).first()

            if user is None:
                messages.error(request, 'No account found with this username.')
                return redirect('forget-password')

        if not user.email:
            messages.error(request, 'No email is connected with this account.')
            return redirect('forget-password')

        # Delete old OTP
        OtpModel.objects.filter(user=user).delete()

        # Generate OTP
        otp = random.randint(1000, 9999)

        # Save OTP
        OtpModel.objects.create(
            user=user,
            otp=otp,
            created_at=timezone.now()
        )

        # Send OTP email safely
        try:
            send_mail(
                'Your OTP for Password Reset',
                f'Your OTP for password reset is {otp}. It is valid for 10 minutes.',
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=False,
            )

        except Exception as e:
            print("OTP EMAIL ERROR:", e)
            messages.error(request, 'OTP could not be sent. Please try again later.')
            return redirect('forget-password')

        messages.success(request, 'OTP has been sent to your registered email.')
        return render(request, 'submitotp.html', {
            'username': user.username
        })


    # SUBMIT OTP
    if request.method == 'POST' and 'submit_otp' in request.POST:
        username = request.POST.get('username')
        otp = request.POST.get('otp')

        user = User.objects.filter(username=username).first()

        if user is None:
            messages.error(request, 'User not found. Please try again.')
            return redirect('forget-password')

        otp_obj = OtpModel.objects.filter(user=user, otp=otp).first()

        if otp_obj is None:
            messages.error(request, 'Invalid OTP.')
            return render(request, 'submitotp.html', {
                'username': user.username
            })

        # OTP expiry check
        if timezone.now() > otp_obj.created_at + timedelta(minutes=10):
            otp_obj.delete()
            messages.error(request, 'OTP expired. Please request a new OTP.')
            return render(request, 'submitotp.html', {
                'username': user.username
            })

        messages.success(request, 'OTP verified successfully.')
        return render(request, 'changepassword.html', {
            'username': user.username
        })


    # RESEND OTP
    if request.method == 'POST' and 'resend_otp' in request.POST:
        username = request.POST.get('username')

        user = User.objects.filter(username=username).first()

        if user is None:
            messages.error(request, 'User not found. Please try again.')
            return redirect('forget-password')

        if not user.email:
            messages.error(request, 'No email is connected with this account.')
            return redirect('forget-password')

        OtpModel.objects.filter(user=user).delete()

        otp = random.randint(1000, 9999)

        OtpModel.objects.create(
            user=user,
            otp=otp,
            created_at=timezone.now()
        )

        try:
            send_mail(
                'Your OTP for Password Reset',
                f'Your OTP for password reset is {otp}. It is valid for 10 minutes.',
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=False,
            )

        except Exception as e:
            print("RESEND OTP EMAIL ERROR:", e)
            messages.error(request, 'OTP could not be resent. Please try again later.')
            return render(request, 'submitotp.html', {
                'username': user.username
            })

        messages.success(request, 'New OTP has been sent to your registered email.')
        return render(request, 'submitotp.html', {
            'username': user.username
        })


    # CHANGE PASSWORD
    if request.method == 'POST' and 'change_password' in request.POST:
        username = request.POST.get('username')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        user = User.objects.filter(username=username).first()

        if user is None:
            messages.error(request, 'User not found. Please try again.')
            return redirect('forget-password')

        if new_password != confirm_password:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'changepassword.html', {
                'username': username
            })

        user.set_password(new_password)
        user.save()

        OtpModel.objects.filter(user=user).delete()

        messages.success(request, 'Password changed successfully. Please login.')
        return redirect('login')

    return render(request, 'forgetpassword.html')
