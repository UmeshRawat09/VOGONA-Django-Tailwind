from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Account, UserProfile
from django.utils.html import format_html

# Register your models here.
class AccountAdmin(UserAdmin):
    list_display = ('email', 'username', 'first_name', 'last_name', 'date_joined', 'last_login', 'is_active')
    list_display_links = ('email', 'username', 'first_name', 'last_name')
    readonly_fields = ('date_joined', 'last_login')
    ordering = ("date_joined",)

    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()

class UserProfileAdmin(admin.ModelAdmin):
    def thumbnail(self, obj):
        if obj.profile_image:
            return format_html(
                '<img src="{}" width="30" height="30" style="border-radius:50%;">',
                obj.profile_image.url
            )
        return format_html('<span style="font-size:24px;">👤</span>')
    thumbnail.short_description = 'Profile Image'
    list_display = ('thumbnail', 'user', 'city', 'state')


admin.site.register(Account, AccountAdmin)
admin.site.register(UserProfile, UserProfileAdmin)