from django.db import models
from django.core.urlresolvers import reverse
from django.conf import settings

# Create your models here.
class List(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True)
    shared_with = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='sharee_lists')

    @property
    def name(self):
        first_item = self.item_set.first()
        return first_item.text

    def get_absolute_url(self):
        return reverse('view_list', args=[self.id])

    @staticmethod
    def create_new(first_item_text, owner=None):
        list_ = List.objects.create()
        list_.owner = owner
        list_.save()
        item = Item.objects.create(text=first_item_text, list=list_)
        return list_

class Item(models.Model):
    text = models.TextField(default='')
    list = models.ForeignKey(List, default=None)

    class Meta:
        ordering = ('id',)
        unique_together = ('list', 'text')

    def __str__(self):
        return self.text