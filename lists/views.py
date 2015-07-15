from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model

from lists.models import Item, List
from lists.forms import ItemForm, ExistingListItemForm, NewListForm

User = get_user_model()

# Create your views here.
def new_list(request):
    form = NewListForm(data=request.POST)
    if form.is_valid():
        list_ = form.save(owner=request.user)
        return redirect(list_)
    return render(request, 'home.html', {'form': form})


def view_list(request, list_id):
    list_ = List.objects.get(id=list_id)
    form = ExistingListItemForm(for_list=list_)

    if request.method == 'POST':
        form = ExistingListItemForm(for_list=list_ ,data=request.POST)
        if form.is_valid():
            item = form.save()
            return redirect(list_)

    return render(request, 'list.html', {"list": list_, "form": form})

def home_page(request):
    return render(request, 'home.html', {'form': ItemForm()})

def my_lists(request, email):
    try:
        owner = User.objects.get(email=email)
    except User.DoesNotExist:
        owner = None

    return render(request, 'my_lists.html', {'owner': owner})
