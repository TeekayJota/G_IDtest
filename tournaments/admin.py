from django.contrib import admin

from .models import Member, Registration, StaffNote, Tournament


class MemberInline(admin.TabularInline):
    model = Member
    extra = 0


class StaffNoteInline(admin.TabularInline):
    model = StaffNote
    extra = 0


@admin.register(Tournament)
class TournamentAdmin(admin.ModelAdmin):
    list_display = ("name", "game", "format", "status", "slots_label", "start_date", "featured")
    list_filter = ("game", "status", "format", "featured")
    search_fields = ("name", "game")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Registration)
class RegistrationAdmin(admin.ModelAdmin):
    list_display = ("code", "display_name", "tournament", "status", "created_at")
    list_filter = ("status", "tournament__game", "tournament")
    search_fields = ("code", "team_name", "first_name", "last_name", "email")
    inlines = [MemberInline, StaffNoteInline]
    readonly_fields = ("created_at",)


@admin.register(StaffNote)
class StaffNoteAdmin(admin.ModelAdmin):
    list_display = ("registration", "author_name", "created_at")
