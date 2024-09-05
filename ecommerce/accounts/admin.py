from django.contrib import admin
from accounts.models import User

# Custom admin for User to handle user management
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('user_id','email', 'first_name', 'last_name', 'is_staff')
    search_fields = ('email', 'first_name', 'last_name')
    list_filter = ('is_staff', 'is_active')
    ordering = ('email',)


admin.site.register(User, CustomUserAdmin)
