from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.template.loader import render_to_string

from lists.models import Item

# Create your views here.
def home_page(request):
    if request.method == 'POST':
        new_item_text = request.POST['item_text']
        Item.objects.create(text=new_item_text)
        return redirect('/')

    items = Item.objects.all()

    return render(request, 'home.html', {'items':items})