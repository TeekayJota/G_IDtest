from django.contrib.auth.views import LogoutView
from django.urls import path

from . import views

urlpatterns = [
    # --- Público ---
    path("", views.landing, name="landing"),
    path("torneos/", views.tournament_list, name="tournament_list"),
    path("torneos/<slug:slug>/", views.tournament_detail, name="tournament_detail"),
    path("inscribirse/", views.register, name="register"),
    path("torneos/<slug:slug>/inscribirse/", views.register, name="register_tournament"),
    path("inscripcion/<str:code>/", views.confirm, name="confirm"),

    # --- Staff ---
    path("staff/", views.StaffLoginView.as_view(), name="staff_login"),
    path("staff/salir/", LogoutView.as_view(), name="staff_logout"),
    path("staff/inscripciones/", views.inbox, name="staff_inbox"),
    path("staff/inscripciones/<str:code>/", views.reg_detail, name="staff_reg_detail"),
    path("staff/torneos/nuevo/", views.create_tournament, name="staff_create"),
]
