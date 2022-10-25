from django.contrib import admin

from .models import CustomUser, Subscription


class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name')
    list_filter = ('username', 'email')
    search_fields = ('username', 'email')


class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'author')
    list_filter = ('user', 'author')


admin.site.register(CustomUser, UserAdmin)
admin.site.register(Subscription, SubscriptionAdmin)
