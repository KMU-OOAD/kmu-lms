from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User

class UserAdmin(BaseUserAdmin):
    # 관리자 페이지에서 표시할 필드 지정
    list_display = ('student_id', 'username', 'email', 'status', 'is_admin')
    list_filter = ('is_admin', 'status')
    fieldsets = (
        (None, {'fields': ('student_id', 'password')}),
        ('개인 정보', {'fields': ('username', 'email', 'phone')}),
        ('권한 설정', {'fields': ('is_admin', 'is_active', 'status')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('student_id', 'username', 'phone', 'email', 'password1', 'password2'),
        }),
    )
    search_fields = ('student_id', 'username', 'email')
    ordering = ('student_id',)
    filter_horizontal = ()

admin.site.register(User, UserAdmin)
