from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required


@login_required(login_url='accounts:login')
def dashboard(request):
    return render(request, 'dashboard.html')


@login_required(login_url='accounts:login')
def module_list(request):
    return render(request, 'modules.html')


@login_required(login_url='accounts:login')
def module_detail(request, pk):
    return render(request, 'modules.html', {'module_pk': pk})


@login_required(login_url='accounts:login')
def lesson_detail(request, module_pk, pk):
    return render(request, 'lesson.html', {'module_pk': module_pk, 'lesson_pk': pk})
