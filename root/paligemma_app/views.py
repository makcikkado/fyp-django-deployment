from django.http import HttpResponse
from django.db import models

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User, AbstractUser
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from django.core.mail import EmailMessage
from django.utils import timezone
from django.urls import reverse
from .models import *
from django.utils.html import format_html
from .inference import query_paligemma
import os

# Create your views here.
def mainView(request):

    if request.method == "POST":
        imagePrompt = request.FILES.get('imagePrompt')
        textPrompt = request.POST.get('textPrompt')

        if imagePrompt and textPrompt:
            new_prompt = Prompt.objects.create(imagePrompt=imagePrompt, textPrompt=textPrompt)
            messages.success(request, "Image uploaded successfully!")
            return redirect('response', pk=new_prompt.pk)
        else:
            messages.error(request, "Failed to upload image. Please try again.")
            return redirect ('main')

    return render (request, 'main.html')    

def ResponseView(request, pk=None):

    if pk is not None:
        try:
            prompt_obj = Prompt.objects.get(pk=pk)
        except Prompt.DoesNotExist:
            messages.error(request, "Prompt not found.")
            return redirect('home')
        
        # Get absolute path to the uploaded image
        image_path = os.path.join(settings.MEDIA_ROOT, str(prompt_obj.imagePrompt))

        # Run the image + prompt through PaliGemma via your inference script
        ai_response = query_paligemma(image_path=image_path, user_prompt=prompt_obj.textPrompt)

        # Save the AI response to the database
        # saved_response = Response.objects.create(
        #     response=ai_response[:50],  # ensure it fits in CharField (max_length=50)
        #     feedback=0,                 # default or placeholder until user gives feedback
        #     prompt=prompt_obj
        # )

        # Optional: also save to History table
        # History.objects.create(
        #     user=request.user,
        #     prompt=prompt_obj,
        #     response=saved_response
        # )

        # Update profile table
        # profile = Profile.objects.get(user=request.user)
        # profile.prompts.add(prompt_obj)
        # profile.responses.add(saved_response)

        context = {
            'prompt': prompt_obj,
            'ai_response': ai_response
            # 'response_obj': saved_response
        }
        return render(request, 'response.html', context)

    return render(request, 'main.html')

    #     context = {
    #         'prompt': prompt_obj
    #     }
    #     return render(request, 'response.html', context)
    # prompt = get_object_or_404(Prompt, pk=pk)
    # return render(request, 'response.html', {'prompt': prompt})

        # apply the HF API       
        # fetch image from database
            # img = Prompt.objects.all()
            # context = {'img': img}
            # return render(request, 'response.html', context)
        # prompt_obj = Prompt.objects.get(pk=pk)
        # return render(request, 'response.html', {'prompt': prompt_obj})
        # fetch prompt from database
        # click 'new chat' then got popup 
    
    return render ('home') 

@login_required(login_url='/login/') #user must be logged in before accessing homepage, can remove this later if not needed, if remove, check settings.py and remove LOGIN_URL variable.
def Home(request):
    return render(request, 'index.html')

def RegisterView(request):

    if request.method == "POST":
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        user_data_has_error = False

        # validations
        # make sure email and username are not being re-used
        if User.objects.filter(username=username).exists():
            user_data_has_error = True
            messages.error(request, "Username already exists")

        if User.objects.filter(email=email).exists():
            user_data_has_error = True
            messages.error(request, "Email already exists")

        # make sure password is at least 5 characters long
        if len(password) < 5:
            user_data_has_error = True
            messages.error(request, "Password must be at least 5 characters")

        if password != confirm_password:
            messages.error(request, "Passwords does not match!")
            return redirect ('register')

        if user_data_has_error:
            return redirect ('register')
        else:
            new_user = User.objects.create_user(
                first_name = first_name,
                last_name = last_name,
                email = email,
                username = username,
                password = password
            )
            messages.success(request, "Account created. Login now")
            return redirect('login')

    return render(request, 'register.html')

def LoginView(request):

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:            #checks if user exists
            login(request, user)

            return redirect('home')         #if user exist, then redirect to homepage (index.html)
        else:
            messages.error(request, "Invalid login credentials")
            return redirect ('login')

    return render(request, 'login.html')

def LogoutView(request):
    logout(request)
    return redirect ('login')

def ForgotPassword(request):

    if request.method == "POST":
        email = request.POST.get('email')

        # verify if email exists
        try:
            user = User.objects.get(email=email)

            # create a new reset id
            new_password_reset = PasswordReset(user=user)
            new_password_reset.save()

            # creat password reset ur;
            password_reset_url = reverse('reset-password', kwargs={'reset_id': new_password_reset.reset_id})

            full_password_reset_url = f'{request.scheme}://{request.get_host()}{password_reset_url}'

            # email content
            email_body = f'Reset your password using the link below:\n\n\n{full_password_reset_url}'

            email_message = EmailMessage(
                'Reset your password', # email subject
                email_body,
                settings.EMAIL_HOST_USER, # email sender
                [email] # email  receiver 
            )

            email_message.fail_silently = True
            email_message.send()

            return redirect('password-reset-sent', reset_id=new_password_reset.reset_id)

        except User.DoesNotExist:
            messages.error(request, f"No user with email '{email}' found")
            return redirect('forgot-password')

    return render(request, 'forgot_password.html')

def PasswordResetSent(request, reset_id):

    if PasswordReset.objects.filter(reset_id=reset_id).exists():
        return render(request, 'password_reset_sent.html')
    else:
        # redirect to forgot password page if code does not exist
        messages.error(request, 'Invalid reset id')
        return redirect('forgot-password')

def ResetPassword(request, reset_id):

    try:
        password_reset_id = PasswordReset.objects.get(reset_id=reset_id)

        if request.method == "POST":
            password = request.POST.get('password')
            confirm_password = request.POST.get('confirm_password')

            passwords_have_error = False

            if password != confirm_password:
                passwords_have_error = True
                messages.error(request, 'Passwords do not match')

            if len(password) < 5:
                passwords_have_error = True
                messages.error(request, 'Password must be at least 5 characters long')

            # check to make sure link has not expired
            expiration_time = password_reset_id.created_when + timezone.timedelta(minutes=10)

            if timezone.now() > expiration_time:
                passwords_have_error = True
                messages.error(request, 'Reset link has expired')

                #delete the reset_id after expiration
                password_reset_id.delete()

            # reset password
            if not passwords_have_error:
                user = password_reset_id.user
                user.set_password(password)
                user.save()

                # delete reset id after use
                password_reset_id.delete()

                # redirect to login
                messages.success(request, 'Password reset. Proceed to login')
                return redirect('login')
            
            else:
                # redirect back to password reset page and display errors
                return redirect('reset-password', reset_id=reset_id)
    
    except PasswordReset.DoesNotExist:
        
        # redirect to forgot password page if code does not exist
        messages.error(request, 'Invalid reset id')
        return redirect('forgot-password')
    
    return render(request, 'reset_password.html')

def HomePageView(request):

    if request.method == "POST":
        imagePrompt = request.FILES.get('imagePrompt')
        textPrompt = request.POST.get('textPrompt')

        if imagePrompt and textPrompt:
            new_prompt = Prompt.objects.create(userID=request.user, imagePrompt=imagePrompt, textPrompt=textPrompt)
            messages.success(request, "Image uploaded successfully!")
            return redirect('response-logged', pk=new_prompt.pk)
        else:
            messages.error(request, "Failed to upload image. Please try again.")
            return redirect ('home')

    return render (request, 'index.html')

def ResponseLoggedView(request, pk=None):

    if pk is not None:
        try:
            prompt_obj = Prompt.objects.get(pk=pk)
        except Prompt.DoesNotExist:
            messages.error(request, "Prompt not found.")
            return redirect('home')
        
        # Get absolute path to the uploaded image
        image_path = os.path.join(settings.MEDIA_ROOT, str(prompt_obj.imagePrompt))

        # Run the image + prompt through PaliGemma via your inference script
        ai_response = query_paligemma(image_path=image_path, user_prompt=prompt_obj.textPrompt)

        # Save the AI response to the database
        saved_response = Response.objects.create(
            response=ai_response[:50],  # ensure it fits in CharField (max_length=50)
            feedback=0,                 # default or placeholder until user gives feedback
            prompt=prompt_obj
        )

        # Optional: also save to History table
        History.objects.create(
            user=request.user,
            prompt=prompt_obj,
            response=saved_response
        )

        # Update profile table
        profile = Profile.objects.get(user=request.user)
        profile.prompt.add(prompt_obj)
        profile.response.add(saved_response)

        context = {
            'prompt': prompt_obj,
            'ai_response': ai_response,
            'response_obj': saved_response
        }
        return render(request, 'response_logged.html', context)

    return render(request, 'home.html')

        # context = {
        #     'prompt': prompt_obj
        # }
        # return render(request, 'response.html', context)
        # prompt = get_object_or_404(Prompt, pk=pk)
        # return render(request, 'response.html', {'prompt': prompt})

        # apply the HF API       
        # fetch image from database
            # img = Prompt.objects.all()
            # context = {'img': img}
            # return render(request, 'response.html', context)
        # prompt_obj = Prompt.objects.get(pk=pk)
        # return render(request, 'response.html', {'prompt': prompt_obj})
        # fetch prompt from database
        # click 'new chat' then got popup 
    
    return render ('home') 

def HistoryView(request):
    # user_prompts = Prompt.objects.filter(userID=request.user).order_by('-promptID')
    # responses = Profile.objects.filter(user=request.user).order_by('-response')
    # context = {
    #     'response': responses
    # }

    profile = Profile.objects.get(user=request.user)
    responses = profile.response.all().select_related('prompt')  # Efficiently fetch linked prompt

    context = {
        'profile': profile,
        'responses': responses
    }
    return render(request, 'history.html', context)

def LanguageView(request):
    return render(request, 'language.html')

def HelpView(request):
    return render(request, 'help-menu.html')
