from django.contrib import admin
from .models import PasswordReset, Prompt


# Register your models here.
class HomeAdmin(admin.ModelAdmin):
    readonly_field = ('id',)

admin.site.register(PasswordReset, HomeAdmin)

class PromptAdmin(admin.ModelAdmin):
    readonly_field = ('id',)

admin.site.register(Prompt, PromptAdmin)