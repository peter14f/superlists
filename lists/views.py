from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.template.loader import render_to_string

from lists.models import Item, List

# Create your views here.
def add_item(request, list_id):
    list_ = List.objects.get(id=list_id)
    Item.objects.create(text=request.POST['item_text'], list=list_)
    return redirect('/lists/%d/' % (list_.id,))

def new_list(request):
    list_ = List.objects.create()
    item_text = request.POST['item_text']
    Item.objects.create(text=item_text, list=list_)
    return redirect('/lists/%d/' % (list_.id,))

def view_list(request, list_id):
    list_ = List.objects.get(id=list_id)
    items = Item.objects.filter(list=list_)
    return render(request, 'list.html', {'list': list_})

def home_page(request):
    return render(request, 'home.html')
