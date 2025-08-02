from .models import Category

def menu_list(request):
    list = Category.objects.all()
    if not list:
        list = []
    return {'list':list}
