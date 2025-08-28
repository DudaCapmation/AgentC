from django.contrib import admin
from apps.core.models import TeamMember,Client

@admin.register(TeamMember)
class TeamMemberAdmin(admin.ModelAdmin):
    list_display = ["first_name", "last_name", "email", "country", "joined_on"]


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ["name", "description", "email"]