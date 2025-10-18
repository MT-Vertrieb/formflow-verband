
from apps.settingsmgr.models import ThemeSettings, GeneralSettings

def theme(request):
    org_name = 'Vereinssystem'
    colors = {
        'primary':'#183153',
        'accent':'#f3f4f6',
        'sidebar':'#0f172a',
        'text':'#111827'
    }
    try:
        gen = GeneralSettings.get_solo()
        org_name = gen.organization_name or org_name
        theme = ThemeSettings.get_solo()
        colors = {
            'primary': theme.primary_color or colors['primary'],
            'accent': theme.accent_color or colors['accent'],
            'sidebar': theme.sidebar_color or colors['sidebar'],
            'text': theme.text_color or colors['text'],
        }
    except Exception:
        pass
    return {'ORG_NAME': org_name, 'THEME_COLORS': colors}
