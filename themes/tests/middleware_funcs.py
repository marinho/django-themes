from themes.models import Theme

def choose_theme(request):
    return Theme.objects.exclude(is_default=True).order_by('pk')[0]

