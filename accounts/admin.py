from django.contrib import admin
from accounts.models import User, Book , Author , Genre , Publisher , qoute, Order, OrderItem
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

class UserAdmin(BaseUserAdmin):
    list_display = ('email', 'fullname', 'is_active', 'is_superuser')
    list_filter = ('is_active', 'is_superuser')
    search_fields = ('email', 'fullname')
    ordering = ('email',)
    fieldsets = (
        (None, {'fields': ('email', 'fullname')}),
        ('اطلاعات شخصی', {'fields': ('address','phone')}),
        ('دسترسی‌ها', {'fields': ('is_active', 'is_superuser', 'groups', 'user_permissions')}),
        ('تاریخ‌ها', {'fields': ('last_login',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'fullname', 'password1', 'password2', 'is_active', 'is_superuser')}
        ),
    )
class CustomAdminSite(admin.AdminSite):
    def get_app_list(self, request):
        app_list = super().get_app_list(request)
        # حذف گروه‌ها از لیست
        app_list = [app for app in app_list if app['name'] != 'Authentication and Authorization']
        return app_list

custom_admin_site = CustomAdminSite(name='custom_admin')

custom_admin_site.register(User, UserAdmin)
admin.site.register(User, UserAdmin)
admin.site.register(Book)
admin.site.register(Author)
admin.site.register(Genre)
admin.site.register(Publisher)
admin.site.register(qoute)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'total_price', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['user__username', 'id']
    readonly_fields = ['created_at']
    date_hierarchy = 'created_at'

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'product', 'quantity', 'price']
    list_select_related = ['order', 'product']
