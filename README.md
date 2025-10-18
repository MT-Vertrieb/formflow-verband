
# Vereinssystem – Phase 0 (Skeleton)

**Ziel:** Lauffähiges Grundgerüst mit E-Mail-Login (Admin-Freigabe), Admin-Einstellungen (Theme/Name/Mails/SharePoint/Mileage/Budgetjahr),
CSV-Importer (Kostenstellen/Cluster) mit Jahr-Overwrite, Theming (Header/Sidebar), SMTP-Test.

## Schnellstart (Entwicklung)
1. Python 3.12, pip, venv bereitstellen.
2. `python -m venv env && source env/bin/activate` (Windows: `env\Scripts\activate`)
3. `pip install -r requirements.txt`
4. `.env` anlegen (siehe `.env.example`).
5. `python manage.py migrate`
6. `python manage.py createsuperuser`
7. `python manage.py runserver` → http://localhost:8000

## .env Beispiel
Siehe `.env.example`. Standardmäßig SQLite. Für Postgres später `DATABASE_URL=postgres://...` setzen.

## Git & GitHub
```bash
git init
git add .
git commit -m "Phase 0: initial skeleton"
# Erstelle ein leeres Repo bei GitHub und ersetze <YOUR-REPO-URL>:
git remote add origin <YOUR-REPO-URL>
git branch -M main
git push -u origin main
```

## Features in Phase 0
- Login via E-Mail + Passwort (Registrierung → Admin-Freigabe nötig)
- Admin-Einstellungen (Theme, Vereinsname, Ziel-E-Mails, SharePoint-Settings, Kilometersätze, Haushaltsplan-Jahre)
- CSV-Importer (Kostenstellen/Cluster) pro Jahr, Dry-Run & Overwrite
- SMTP-Test (Admin-only)
- Basis-Layout (Header mit Vereinsname, ausfahrbare Sidebar)

## Nächste Phasen
- Profile, Rollen/Scopes, echte Workflows etc. (siehe Roadmap)
