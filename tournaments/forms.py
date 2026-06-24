from django import forms

from .models import Registration, Tournament

# Atributos de estilo que replican los inputs del prototipo.
INPUT_ATTRS = {"class": "field"}
SELECT_ATTRS = {"class": "field"}
TEXTAREA_ATTRS = {"class": "field", "rows": 4}

PLACEHOLDERS = {
    "team_name": "Nombre del equipo",
    "first_name": "Mateo",
    "last_name": "Quispe",
    "dni": "74852136",
    "phone": "+51 987 654 321",
    "email": "tu@correo.com",
    "steam_id": "STEAM_0:1:48205",
    "nick": "tu_nick",
    "gaming_center": "Cyber Arena – Miraflores",
}


class RegistrationForm(forms.ModelForm):
    """Formulario público de inscripción.

    Los campos se adaptan al torneo: equipo vs individual y qué datos pide.
    """

    class Meta:
        model = Registration
        fields = [
            "team_name", "first_name", "last_name", "dni",
            "phone", "email", "steam_id", "nick", "gaming_center",
        ]

    def __init__(self, *args, tournament=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.tournament = tournament

        for name, field in self.fields.items():
            field.widget.attrs.setdefault("class", "field")
            if name in PLACEHOLDERS:
                field.widget.attrs.setdefault("placeholder", PLACEHOLDERS[name])

        if not tournament:
            return

        # Equipo vs individual.
        if tournament.requires_team:
            self.fields["team_name"].required = True
        else:
            self.fields.pop("team_name", None)

        # Campos opcionales según la configuración del torneo.
        optional_map = {
            "dni": tournament.field_dni,
            "phone": tournament.field_phone,
            "email": tournament.field_email,
            "steam_id": tournament.field_steam,
            "nick": tournament.field_nick,
            "gaming_center": tournament.field_gaming_center,
        }
        for name, enabled in optional_map.items():
            if not enabled:
                self.fields.pop(name, None)

        self.fields["first_name"].required = True
        if "last_name" in self.fields:
            self.fields["last_name"].required = True


class TournamentForm(forms.ModelForm):
    """Formulario de creación de torneo (staff/admin)."""

    class Meta:
        model = Tournament
        fields = [
            "name", "game", "format", "team_size",
            "slots_total", "prize_pen",
            "start_date", "end_date", "registration_close",
            "code_prefix", "status", "featured", "description",
            "field_dni", "field_phone", "field_email",
            "field_steam", "field_nick", "field_gaming_center",
        ]
        widgets = {
            "name": forms.TextInput(attrs={**INPUT_ATTRS, "placeholder": "Beyond The Dreams · Dota 2"}),
            "game": forms.Select(attrs=SELECT_ATTRS),
            "format": forms.Select(attrs=SELECT_ATTRS),
            "team_size": forms.NumberInput(attrs={**INPUT_ATTRS, "placeholder": "5"}),
            "slots_total": forms.NumberInput(attrs={**INPUT_ATTRS, "placeholder": "32"}),
            "prize_pen": forms.NumberInput(attrs={**INPUT_ATTRS, "placeholder": "2000"}),
            "start_date": forms.DateInput(attrs={**INPUT_ATTRS, "type": "date"}),
            "end_date": forms.DateInput(attrs={**INPUT_ATTRS, "type": "date"}),
            "registration_close": forms.DateTimeInput(
                attrs={**INPUT_ATTRS, "type": "datetime-local"}, format="%Y-%m-%dT%H:%M"
            ),
            "code_prefix": forms.TextInput(attrs={**INPUT_ATTRS, "placeholder": "BTD"}),
            "status": forms.Select(attrs=SELECT_ATTRS),
            "description": forms.Textarea(
                attrs={**TEXTAREA_ATTRS, "placeholder": "Formato de doble eliminación, BO3 en playoffs…"}
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["registration_close"].input_formats = ["%Y-%m-%dT%H:%M"]
