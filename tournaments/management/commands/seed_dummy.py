"""Carga datos de PRUEBA (torneos + inscripciones) de forma SEGURA.

A diferencia de `seed_demo` (que borra todo y es solo para desarrollo), este
comando:
  - NO borra datos existentes.
  - NO crea/resetea usuarios (tu admin real queda intacto).
  - Es idempotente: si los datos ya existen, no los duplica.

Pensado para producción: que el cliente tenga torneos e inscripciones con qué
jugar. Se ejecuta solo si la variable SEED_DUMMY es verdadera (o con --force).

    python manage.py seed_dummy --force      # manual (consola de Railway)
"""

import os
from datetime import date, datetime

from django.core.management.base import BaseCommand
from django.utils import timezone

from tournaments.models import Member, Registration, StaffNote, Tournament


def aware(y, m, d, hh=0, mm=0):
    return timezone.make_aware(datetime(y, m, d, hh, mm))


def _truthy(val):
    return (val or "").strip().lower() in {"1", "true", "yes", "on"}


class Command(BaseCommand):
    help = "Carga torneos e inscripciones de prueba sin borrar nada (idempotente)."

    def add_arguments(self, parser):
        parser.add_argument("--force", action="store_true",
                            help="Ejecuta aunque SEED_DUMMY no esté definida.")

    def handle(self, *args, **options):
        if not options["force"] and not _truthy(os.environ.get("SEED_DUMMY")):
            self.stdout.write("seed_dummy: SEED_DUMMY no activa, se omite (usa --force para forzar).")
            return

        created_t = self._tournaments()
        created_r = self._registrations()
        self.stdout.write(self.style.SUCCESS(
            f"seed_dummy: listo (torneos nuevos: {created_t}, inscripciones nuevas: {created_r})."
        ))

    # --- Torneos --------------------------------------------------------------
    def _tournaments(self):
        data = [
            dict(slug="dota-2", name="Dota 2", game="Dota 2",
                 format=Tournament.Format.TEAM, team_size=5,
                 start_date=date(2026, 6, 7), end_date=date(2026, 6, 9),
                 registration_close=aware(2026, 6, 5, 23, 59),
                 prize_pen=2000, slots_total=32, slots_taken=24,
                 status=Tournament.Status.OPEN, featured=True, code_prefix="BTD",
                 field_dni=True, field_phone=True, field_email=True,
                 field_steam=True, field_nick=False, field_gaming_center=True,
                 description=("Torneo oficial 5 vs 5. Doble eliminación, BO3 en "
                              "playoffs y gran final BO5. Inscripción por equipos.")),
            dict(slug="fortnite", name="Fortnite", game="Fortnite",
                 format=Tournament.Format.DUO, team_size=2,
                 start_date=date(2026, 6, 10), end_date=date(2026, 6, 11),
                 registration_close=aware(2026, 6, 9, 23, 59),
                 prize_pen=1500, slots_total=64, slots_taken=48,
                 status=Tournament.Status.OPEN, code_prefix="BTD",
                 field_dni=True, field_phone=True, field_email=True,
                 field_steam=False, field_nick=True, field_gaming_center=True,
                 description="Torneo de dúos. Puntuación por partidas."),
            dict(slug="efootball", name="eFootball", game="eFootball",
                 format=Tournament.Format.SOLO, team_size=1,
                 start_date=date(2026, 6, 12), end_date=date(2026, 6, 12),
                 registration_close=aware(2026, 6, 11, 23, 59),
                 prize_pen=1000, slots_total=64, slots_taken=58,
                 status=Tournament.Status.FEW, code_prefix="BTD",
                 field_dni=True, field_phone=True, field_email=True,
                 field_steam=False, field_nick=True, field_gaming_center=True,
                 description="Torneo individual 1 vs 1. Eliminación directa."),
            dict(slug="clash-royale", name="Clash Royale", game="Clash Royale",
                 format=Tournament.Format.SOLO, team_size=1,
                 start_date=date(2026, 6, 14), end_date=date(2026, 6, 14),
                 registration_close=aware(2026, 6, 13, 23, 59),
                 prize_pen=500, slots_total=64, slots_taken=0,
                 status=Tournament.Status.SOON, code_prefix="BTD",
                 field_dni=True, field_phone=True, field_email=True,
                 field_steam=False, field_nick=True, field_gaming_center=True,
                 description="Torneo individual 1 vs 1. Próximamente."),
        ]
        n = 0
        for d in data:
            slug = d.pop("slug")
            _, created = Tournament.objects.get_or_create(slug=slug, defaults=d)
            n += int(created)
        return n

    # --- Inscripciones --------------------------------------------------------
    def _registrations(self):
        dota = Tournament.objects.get(slug="dota-2")
        fortnite = Tournament.objects.get(slug="fortnite")
        efootball = Tournament.objects.get(slug="efootball")
        clash = Tournament.objects.get(slug="clash-royale")
        S = Registration.Status

        teams = [
            ("BTD-0241", "Lima Strikers", "Mateo", "Quispe", S.PENDING, aware(2026, 5, 26, 14, 2),
             dict(dni="74852136", phone="+51 987 654 321", email="mateo.quispe@correo.com",
                  steam_id="STEAM_0:1:48205", nick="mateoQ", gaming_center="Cyber Arena – Miraflores"),
             [("shadowJP", "STEAM_0:1:55120", "70231458"), ("kira_07", "STEAM_0:0:99214", "76554120"),
              ("andesPro", "STEAM_0:1:31077", "72004587"), ("lima_mid", "STEAM_0:0:62318", "75889033")]),
            ("BTD-0238", "Andean Wolves", "J.", "Huamán", S.APPROVED, aware(2026, 5, 26, 11, 40),
             dict(steam_id="STEAM_0:1:20011", gaming_center="LanZone – Lima", nick="huaman_cap"), None),
            ("BTD-0228", "Inca Gaming", "R.", "Ccora", S.REVIEW, aware(2026, 5, 24, 20, 5),
             dict(steam_id="STEAM_0:0:33442", gaming_center="Cyber Inca – Cusco", nick="ccora"), None),
            ("BTD-0233", "Selva Squad", "D.", "Ríos", S.REJECTED, aware(2026, 5, 25, 16, 55),
             dict(steam_id="STEAM_0:1:77881", gaming_center="GG Center – Iquitos", nick="rios_d"), None),
            ("BTD-0219", "Pacific Five", "L.", "Vargas", S.APPROVED, aware(2026, 5, 23, 18, 0),
             dict(steam_id="STEAM_0:0:90211", gaming_center="NetPlay – Callao", nick="vargas_l"), None),
            ("BTD-0221", "Cusco Esports", "A.", "Mamani", S.PENDING, aware(2026, 5, 23, 20, 0),
             dict(steam_id="STEAM_0:1:12009", gaming_center="Andes Gaming – Cusco", nick="mamani"),
             [("cusco_2", "STEAM_0:0:44521", ""), ("cusco_3", "STEAM_0:1:44600", "")]),
        ]
        n = 0
        lima = None
        for code, team_name, fn, ln, status, created, extra, members in teams:
            reg, was = Registration.objects.get_or_create(
                code=code,
                defaults=dict(tournament=dota, team_name=team_name, first_name=fn,
                              last_name=ln, status=status, created_at=created, **extra),
            )
            if was:
                n += 1
                for i, (nick, steam, dni) in enumerate(members or [], start=2):
                    Member.objects.create(registration=reg, nick=nick, steam_id=steam, dni=dni, order=i)
            if code == "BTD-0241":
                lima = reg

        singles = [
            (efootball, "BTD-0235", "", "Mateo", "Salas", S.REVIEW, aware(2026, 5, 25, 19, 10),
             dict(dni="71239845", phone="+51 986 123 456", email="mateo.salas@correo.com",
                  nick="mateoGOL", gaming_center="Cyber Sur – Arequipa")),
            (fortnite, "BTD-0230", "Dúo Ríos", "Valeria", "Ríos", S.PENDING, aware(2026, 5, 25, 12, 20),
             dict(dni="70998123", phone="+51 985 654 321", email="valeria.rios@correo.com",
                  nick="valeRZ", gaming_center="PlayZone – Trujillo")),
            (clash, "BTD-0225", "", "Diego", "Flores", S.APPROVED, aware(2026, 5, 24, 9, 30),
             dict(dni="72556198", phone="+51 984 222 333", email="diego.flores@correo.com",
                  nick="diegoCR", gaming_center="GameHub – Lima")),
        ]
        for tour, code, team_name, fn, ln, status, created, extra in singles:
            _, was = Registration.objects.get_or_create(
                code=code,
                defaults=dict(tournament=tour, team_name=team_name, first_name=fn,
                              last_name=ln, status=status, created_at=created, **extra),
            )
            n += int(was)

        # Notas internas de ejemplo (solo si Lima Strikers se creó y aún no tiene).
        if lima and not lima.notes.exists():
            StaffNote.objects.create(
                registration=lima, author_label="Carla (Admin)",
                text="Faltan confirmar los datos del capitán; el DNI no coincide con el registro.",
                created_at=aware(2026, 5, 26, 14, 30))
            StaffNote.objects.create(
                registration=lima, author_label="Luis (Staff)",
                text="Solicité los datos correctos por WhatsApp al capitán. Quedo a la espera.",
                created_at=aware(2026, 5, 26, 15, 5))
        return n
