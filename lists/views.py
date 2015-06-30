from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.core.exceptions import ValidationError

from lists.models import Item, List
from lists.forms import ItemForm

# Create your views here.
def new_list(request):
    list_ = List.objects.create()
    item_text = request.POST['item_text']
    item = Item(text=item_text, list=list_)

    try:
        item.full_clean()
        item.save()
    except ValidationError:
        list_.delete()
        error = "You can't have an empty list item"
        return render(request, 'home.html', {"error": error})

    return redirect(list_)

def view_list(request, list_id):
    list_ = List.objects.get(id=list_id)

    if request.method == 'POST':
        item_text = request.POST['item_text']
        item = Item(text=item_text, list=list_)
        try:
            item.full_clean()
            item.save()
            return redirect(list_)
        except ValidationError:
            error = "You can't have an empty list item"
            return render(
                request,
                'list.html',
                {"list": list_,
                 "error": error}
            )

    return render(request, 'list.html', {'list': list_})

def home_page(request):
    return render(request, 'home.html', {'form': ItemForm()})
