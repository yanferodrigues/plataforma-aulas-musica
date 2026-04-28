from django.shortcuts import render
from django.contrib.auth.decorators import login_required


@login_required(login_url='accounts:login')
def achievements(request):
    return render(request, 'achievements.html')
