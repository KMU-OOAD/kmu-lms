# notices/views.py
from django.shortcuts import render, get_object_or_404, redirect
from .models import Notice
from .forms import NoticeForm
from django.contrib.auth.decorators import user_passes_test

def notice_list(request):
    notices = Notice.objects.order_by('-posted_date')
    return render(request, 'notices/list.html', {'notices': notices})

def notice_detail(request, pk):
    notice = get_object_or_404(Notice, pk=pk)
    return render(request, 'notices/detail.html', {'notice': notice})

# 관리자만 접근 가능하게
def is_admin(user):
    return user.is_authenticated and user.is_admin

@user_passes_test(is_admin)
def notice_create(request):
    if request.method == 'POST':
        form = NoticeForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('notice_list')
    else:
        form = NoticeForm()
    return render(request, 'notices/form.html', {'form': form})

@user_passes_test(is_admin)
def notice_edit(request, pk):
    notice = get_object_or_404(Notice, pk=pk)
    if request.method == 'POST':
        form = NoticeForm(request.POST, instance=notice)
        if form.is_valid():
            form.save()
            return redirect('notice_detail', pk=pk)
    else:
        form = NoticeForm(instance=notice)
    return render(request, 'notices/form.html', {'form': form})

@user_passes_test(is_admin)
def notice_delete(request, pk):
    notice = get_object_or_404(Notice, pk=pk)
    if request.method == 'POST':
        notice.delete()
        return redirect('notice_list')
    return render(request, 'notices/confirm_delete.html', {'notice': notice})
