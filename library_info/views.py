from django.shortcuts import render, get_object_or_404, redirect
from .models import LibraryInfo
from .forms import LibraryInfoForm
from django.contrib.auth.decorators import user_passes_test

def is_admin(user):
    return user.is_authenticated and user.is_admin

def library_info_list(request):
    infos = sorted(LibraryInfo.objects.all(), key=lambda info: info.day_order)
    return render(request, 'library_info/list.html', {'infos': infos})

@user_passes_test(is_admin)
def library_info_edit(request, day):
    info = get_object_or_404(LibraryInfo, day=day)
    if request.method == 'POST':
        form = LibraryInfoForm(request.POST, instance=info)
        if form.is_valid():
            form.save()
            return redirect('library_info_list')
    else:
        form = LibraryInfoForm(instance=info)
    return render(request, 'library_info/form.html', {'form': form})
