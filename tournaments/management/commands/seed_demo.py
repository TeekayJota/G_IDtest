"""Carga los datos de demostración del prototipo GamerID.

Uso:  python manage.py seed_demo
Borra torneos/inscripciones existentes y los vuelve a crear, además de
asegurar los usuarios de staff. Es idempotente.
"""

from datetime import date, datetime

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils import timezone

from tournaments.models import Member, Registration, StaffNote, Tournament

User = get_user_model()

PASSWORD = "gamerid2026"


def aware(y, m, d, hh=0, mm=0):
    return timezone.make_aware(datetime(y, m, d, hh, mm))


class Command(BaseCommand):
    help = "Crea datos demo (torneos, inscripciones, staff) del prototipo."

    def handle(self, *args, **options):
        self.stdout.write("Limpiando datos previos...")
        StaffNote.objects.all().delete()
        Member.objects.all().delete()
        Registration.objects.all().delete()
        Tournament.objects.all().delete()

        # --- Usuarios de staff -------------------------------------------------
        admin, _ = User.objects.update_or_create(
            username="admin",
            defaults={"first_name": "Admin", "last_name": "GamerID", "email": "admin@gamerid.gg",
                      "role": User.Role.ADMIN, "is_staff": True, "is_superuser": True},
        )
        admin.set_password(PASSWORD)
        admin.save()

        carla, _ = User.objects.update_or_create(
            username="carla@gamerid.gg",
            defaults={"first_name": "Carla", "last_name": "L.", "email": "carla@gamerid.gg",
                      "role": User.Role.ADMIN, "is_staff": True},
        )
        carla.set_password(PASSWORD)
        carla.save()

        luis, _ = User.objects.update_or_create(
            username="luis@gamerid.gg",
            defaults={"first_name": "Luis", "last_name": "R.", "email": "luis@gamerid.gg",
                      "role": User.Role.STAFF, "is_staff": False},
        )
        luis.set_password(PASSWORD)
        luis.save()

        # --- Torneos -----------------------------------------------------------
        dota = Tournament.objects.create(
            name="Dota 2", game="Dota 2", format=Tournament.Format.TEAM, team_size=5,
            start_date=date(2026, 6, 7), end_date=date(2026, 6, 9),
            registration_close=aware(2026, 6, 5, 23, 59),
            prize_pen=2000, slots_total=32, slots_taken=24, status=Tournament.Status.OPEN,
            featured=True, code_prefix="BTD",
            field_dni=True, field_phone=True, field_email=True,
            field_steam=True, field_nick=False, field_gaming_center=True,
            description=("Torneo oficial 5 vs 5. Formato de doble eliminación, BO3 en "
                         "playoffs y gran final BO5. Inscripción por equipos."),
        )
        fortnite = Tournament.objects.create(
            name="Fortnite", game="Fortnite", format=Tournament.Format.DUO, team_size=2,
            start_date=date(2026, 6, 10), end_date=date(2026, 6, 11),
            registration_close=aware(2026, 6, 9, 23, 59),
            prize_pen=1500, slots_total=64, slots_taken=48, status=Tournament.Status.OPEN,
            code_prefix="BTD",
            field_dni=True, field_phone=True, field_email=True,
            field_steam=False, field_nick=True, field_gaming_center=True,
            description="Torneo de dúos. Puntuación por partidas. Inscripción en pareja.",
        )
        efootball = Tournament.objects.create(
            name="eFootball", game="eFootball", format=Tournament.Format.SOLO, team_size=1,
            start_date=date(2026, 6, 12), end_date=date(2026, 6, 12),
            registration_close=aware(2026, 6, 11, 23, 59),
            prize_pen=1000, slots_total=64, slots_taken=58, status=Tournament.Status.FEW,
            code_prefix="BTD",
            field_dni=True, field_phone=True, field_email=True,
            field_steam=False, field_nick=True, field_gaming_center=True,
            description="Torneo individual 1 vs 1. Eliminación directa.",
        )
        Tournament.objects.create(
            name="Clash Royale", game="Clash Royale", format=Tournament.Format.SOLO, team_size=1,
            start_date=date(2026, 6, 14), end_date=date(2026, 6, 14),
            registration_close=aware(2026, 6, 13, 23, 59),
            prize_pen=500, slots_total=64, slots_taken=0, status=Tournament.Status.SOON,
            code_prefix="BTD",
            field_dni=True, field_phone=True, field_email=True,
            field_steam=False, field_nick=True, field_gaming_center=True,
            description="Torneo individual 1 vs 1. Próximamente.",
        )

        # --- Inscripciones de equipo (Dota) ------------------------------------
        def team(code, name, cap_first, cap_last, status, players, created, **extra):
            reg = Registration.objects.create(
                tournament=dota, code=code, team_name=name,
                first_name=cap_first, last_name=cap_last, status=status,
                created_at=created,
                dni=extra.get("dni", ""), phone=extra.get("phone", ""),
                email=extra.get("email", ""), steam_id=extra.get("steam", ""),
                nick=extra.get("nick", ""), gaming_center=extra.get("center", ""),
            )
            members = extra.get("members")
            if members is None:
                members = [(f"jugador_{i}", f"STEAM_0:0:{10000 + i}", "") for i in range(2, players + 1)]
            for i, (nick, steam, dni) in enumerate(members, start=2):
                Member.objects.create(registration=reg, nick=nick, steam_id=steam, dni=dni, order=i)
            return reg

        lima = team(
            "BTD-0241", "Lima Strikers", "Mateo", "Quispe", Registration.Status.PENDING, 5,
            aware(2026, 5, 26, 14, 2),
            dni="74852136", phone="+51 987 654 321", email="mateo.quispe@correo.com",
            steam="STEAM_0:1:48205", nick="mateoQ", center="Cyber Arena – Miraflores",
            members=[
                ("shadowJP", "STEAM_0:1:55120", "70231458"),
                ("kira_07", "STEAM_0:0:99214", "76554120"),
                ("andesPro", "STEAM_0:1:31077", "72004587"),
                ("lima_mid", "STEAM_0:0:62318", "75889033"),
            ],
        )
        team("BTD-0238", "Andean Wolves", "J.", "Huamán", Registration.Status.APPROVED, 5,
             aware(2026, 5, 26, 11, 40), steam="STEAM_0:1:20011", center="LanZone – Lima",
             phone="+51 987 111 222", email="andeanwolves@correo.com", nick="huaman_cap")
        team("BTD-0228", "Inca Gaming", "R.", "Ccora", Registration.Status.REVIEW, 5,
             aware(2026, 5, 24, 20, 5), steam="STEAM_0:0:33442", center="Cyber Inca – Cusco",
             phone="+51 987 333 444", email="incagaming@correo.com", nick="ccora")
        team("BTD-0233", "Selva Squad", "D.", "Ríos", Registration.Status.REJECTED, 5,
             aware(2026, 5, 25, 16, 55), steam="STEAM_0:1:77881", center="GG Center – Iquitos",
             phone="+51 987 555 666", email="selvasquad@correo.com", nick="rios_d")
        team("BTD-0219", "Pacific Five", "L.", "Vargas", Registration.Status.APPROVED, 5,
             aware(2026, 5, 23, 18, 0), steam="STEAM_0:0:90211", center="NetPlay – Callao",
             phone="+51 987 777 888", email="pacificfive@correo.com", nick="vargas_l")
        team("BTD-0221", "Cusco Esports", "A.", "Mamani", Registration.Status.PENDING, 4,
             aware(2026, 5, 23, 20, 0), steam="STEAM_0:1:12009", center="Andes Gaming – Cusco",
             phone="+51 987 999 000", email="cuscoesports@correo.com", nick="mamani")

        # --- Inscripciones individuales / dúo ----------------------------------
        Registration.objects.create(
            tournament=efootball, code="BTD-0235", first_name="Mateo", last_name="Salas",
            status=Registration.Status.REVIEW, created_at=aware(2026, 5, 25, 19, 10),
            dni="71239845", phone="+51 986 123 456", email="mateo.salas@correo.com",
            nick="mateoGOL", gaming_center="Cyber Sur – Arequipa",
        )
        Registration.objects.create(
            tournament=fortnite, code="BTD-0230", team_name="Dúo Ríos", first_name="Valeria", last_name="Ríos",
            status=Registration.Status.PENDING, created_at=aware(2026, 5, 25, 12, 20),
            dni="70998123", phone="+51 985 654 321", email="valeria.rios@correo.com",
            nick="valeRZ", gaming_center="PlayZone – Trujillo",
        )
        Member.objects.create(
            registration=Registration.objects.get(code="BTD-0230"),
            nick="rios_duo2", order=2,
        )
        Registration.objects.create(
            tournament=Tournament.objects.get(name="Clash Royale"), code="BTD-0225",
            first_name="Diego", last_name="Flores",
            status=Registration.Status.APPROVED, created_at=aware(2026, 5, 24, 9, 30),
            dni="72556198", phone="+51 984 222 333", email="diego.flores@correo.com",
            nick="diegoCR", gaming_center="GameHub – Lima",
        )

        # --- Notas internas del staff (sobre Lima Strikers) --------------------
        StaffNote.objects.create(
            registration=lima, author=carla, author_label="Carla (Admin)",
            text="Faltan confirmar los datos del capitán; el DNI no coincide con el del registro.",
            created_at=aware(2026, 5, 26, 14, 30),
        )
        StaffNote.objects.create(
            registration=lima, author=luis, author_label="Luis (Staff)",
            text="Solicité los datos correctos por WhatsApp al capitán. Quedo a la espera.",
            created_at=aware(2026, 5, 26, 15, 5),
        )

        self.stdout.write(self.style.SUCCESS("\n[OK] Datos demo cargados."))
        self.stdout.write("\nAccesos de staff (password: %s):" % PASSWORD)
        self.stdout.write("  - Admin  -> admin               (tambien /admin de Django)")
        self.stdout.write("  - Admin  -> carla@gamerid.gg")
        self.stdout.write("  - Staff  -> luis@gamerid.gg")
