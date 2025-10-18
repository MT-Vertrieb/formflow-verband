import csv, io, re
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import user_passes_test, login_required
from django.contrib import messages
from .forms import CSVUploadForm
from .models import CostCenter, CostCluster

def admin_required(user):
    return user.is_superuser

@login_required
@user_passes_test(admin_required)
def import_csv(request):
    ctx = {'form': CSVUploadForm()}
    if request.method == 'POST':
        form = CSVUploadForm(request.POST, request.FILES)
        if form.is_valid():
            year = form.cleaned_data['year']
            testlauf = form.cleaned_data['dry_run']  # bleibt technisch "dry_run"
            kind = form.cleaned_data['kind']
            file = form.cleaned_data['file']

            raw = file.read().decode('utf-8', errors='ignore')
            first_line = next((ln for ln in raw.splitlines() if ln.strip()), '')
            if ';' not in first_line:
                messages.error(
                    request,
                    "Die CSV muss mit Semikolon (;) getrennt sein. "
                    "Bitte exportiere aus Excel mit Semikolon als Trennzeichen."
                )
                return render(request, 'finance/import.html', {'form': form})

            reader = csv.DictReader(io.StringIO(raw), delimiter=';')
            required = ['code', 'name']
            if kind == 'clusters':
                required.append('costcenter_code')

            missing = [col for col in required if col not in (reader.fieldnames or [])]
            if missing:
                messages.error(request, f"Fehlende Spalten: {', '.join(missing)}. "
                                        f"Erwartet werden: {', '.join(required)} (Semikolon-getrennt).")
                return render(request, 'finance/import.html', {'form': form})

            digits = re.compile(r'^\d+$')
            created = 0
            rows = list(reader)

            if not rows:
                messages.error(request, 'CSV enthält keine Datenzeilen.')
                return render(request, 'finance/import.html', {'form': form})

            if not testlauf:
                if kind == 'costcenters':
                    CostCenter.objects.filter(year=year).delete()
                else:
                    CostCluster.objects.filter(year=year).delete()

            for r in rows:
                code = (r.get('code') or '').strip()
                name = (r.get('name') or '').strip()
                if not digits.match(code):
                    messages.error(request, f"Ungültiger Code (nur Ziffern): {code}")
                    return render(request, 'finance/import.html', {'form': form})

                if kind == 'costcenters':
                    if not testlauf:
                        CostCenter.objects.create(year=year, code=code, name=name)
                    created += 1
                else:
                    cc_code = (r.get('costcenter_code') or '').strip()
                    if not digits.match(cc_code):
                        messages.error(request, f"Ungültige Kostenstelle (nur Ziffern): {cc_code}")
                        return render(request, 'finance/import.html', {'form': form})
                    if not testlauf:
                        cc, _ = CostCenter.objects.get_or_create(
                            year=year, code=cc_code, defaults={'name': f'CC {cc_code}'}
                        )
                        CostCluster.objects.create(year=year, code=code, name=name, cost_center=cc)
                    created += 1

            messages.success(request, f"Import {'(Testlauf) ' if testlauf else ''}erfolgreich: {created} Einträge.")
            if not testlauf:
                return redirect('finance_import')

            ctx['preview'] = rows[:10]
            ctx['created'] = created
        else:
            ctx['form'] = form
    return render(request, 'finance/import.html', ctx)
