from django.shortcuts import render
from django.contrib.auth.decorators import login_required


@login_required(login_url='accounts:login')
def progress(request):
    return render(request, 'progress.html')
