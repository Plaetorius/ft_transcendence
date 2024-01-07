from django.shortcuts import render

def user_profile_view(request):
    return render(request, "users/profile.html") # Django automatically looks inside the app's template folder   