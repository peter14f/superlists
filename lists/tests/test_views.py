from unittest import skip
from unittest.mock import Mock, patch

from django.core.urlresolvers import reverse
from django.test import TestCase
from django.http import HttpRequest
from django.template.loader import render_to_string
from django.utils.html import escape
from django.contrib.auth import get_user_model

from lists.views import home_page, new_list, view_list
from lists.models import Item, List
from lists.forms import (
    DUPLICATE_ITEM_ERROR, EMPTY_LIST_ERROR,
    ExistingListItemForm, ItemForm,
)

User = get_user_model()

# Create your tests here.
class NewListViewIntegratedTest(TestCase):

    def test_saving_a_POST_request(self):
        self.client.post(
            '/lists/new',
            data={'text': 'A new list item'}
        )
        self.assertEqual(Item.objects.count(), 1)
        new_item = Item.objects.first()
        self.assertEqual(new_item.text, 'A new list item')

    def test_invalid_input_doesnt_save_but_shows_errors(self):
        response = self.client.post(
            '/lists/new',
            data={'text': ''}
        )
        self.assertEqual(List.objects.count(), 0)
        self.assertContains(response, escape(EMPTY_LIST_ERROR))

    def test_save_list_owner_if_user_logged_in(self):
        request = HttpRequest()
        request.user = User.objects.create(email='a@b.com')
        request.POST['text'] = 'new list item'
        new_list(request)
        list_ = List.objects.first()
        self.assertEqual(list_.owner, request.user)

    @skip
    def test_redirects_after_POST(self):
        response = self.client.post(
            '/lists/new',
            data={'text': 'A new list item'}
        )
        new_list = List.objects.first()
        self.assertRedirects(response, '/lists/%d/' % (new_list.id,))

    @skip
    def test_for_invalid_input_renders_home_template(self):
        response = self.client.post(
            '/lists/new',
            data={'text': ''}
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home.html')


    @skip
    def test_for_invalid_input_passes_form_to_template(self):
        response = self.client.post(
            '/lists/new',
            data={'text':''}
        )
        self.assertIsInstance(response.context['form'], ItemForm)

    @skip
    def test_validation_errors_are_sent_back_to_home_page_template(self):
        response = self.client.post(
            '/lists/new',
            data={'text': ''}
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home.html')
        expected_error = escape("You can't have an empty list item")
        self.assertContains(response, expected_error)

    @skip
    def test_invalid_list_items_arent_saved(self):
        response = self.client.post(
            '/lists/new',
            data={'text': ''}
        )
        self.assertEqual(List.objects.count(), 0)
        self.assertEqual(Item.objects.count(), 0)

    @skip
    @patch('lists.views.List')
    def test_list_owner_is_saved_if_user_is_authenticated_mock(self, mockList):
        mock_list = List.objects.create()
        mock_list.save = Mock()

        mockList.return_value = mock_list

        request = HttpRequest()

        request.user = User.objects.create()
        request.POST['text'] = 'new list item'

        new_list(request)

        self.assertEqual(mock_list.owner, request.user)

    @skip
    @patch('lists.views.List')
    def test_list_owner_is_saved_if_user_is_authenticated_mock_right_order(self, mockList):
        mock_list = List.objects.create()
        mock_list.save = Mock()
        mockList.return_value = mock_list

        request = HttpRequest()

        request.user = Mock()
        request.user.is_authenticated.return_value = True
        request.POST['text'] = 'new list item'

        def check_owner_assigned():
            self.assertEqual(mock_list.owner, request.user)

        mock_list.save.side_effect = check_owner_assigned

        new_list(request)

@patch('lists.views.NewListForm')
class NewListViewUnitTest(TestCase):

    def setUp(self):
        self.request = HttpRequest()
        self.request.POST['text'] = 'new list item'
        self.request.user = Mock()

    def test_passes_POST_data_to_NewListForm(self, mockNewListForm):
        new_list(self.request)
        mockNewListForm.assert_called_once_with(data=self.request.POST)

    def test_saves_form_with_owner_if_form_valid(self, mockNewListForm):
        mock_form = mockNewListForm.return_value
        mock_form.is_valid.return_value = True
        new_list(self.request)
        mock_form.save.assert_called_once_with(owner=self.request.user)

    @patch('lists.views.redirect')
    def test_redirects_to_form_returned_object_if_form_valid(
            self, mock_redirect, mockNewListForm
    ):
        mock_form = mockNewListForm.return_value
        mock_form.is_valid.return_value = True

        response = new_list(self.request)

        self.assertEqual(response, mock_redirect.return_value)
        mock_redirect.assert_called_once_with(mock_form.save.return_value)

    @patch('lists.views.render')
    def test_renders_home_template_with_form_if_form_invalid(
            self, mock_render, mockNewListForm
    ):
        mock_form = mockNewListForm.return_value
        mock_form.is_valid.return_value = False

        response = new_list(self.request)

        self.assertEqual(response, mock_render.return_value)
        mock_render.assert_called_once_with(
            self.request, 'home.html', {'form': mock_form}
        )

    def test_does_not_save_if_form_invalid(self, mockNewListForm):
        mock_form = mockNewListForm.return_value
        mock_form.is_valid.return_value = False
        new_list(self.request)
        self.assertFalse(mock_form.save.called)

class ListViewTest(TestCase):
    def test_passes_correct_list_to_template(self):
        other_list = List.objects.create()
        correct_list = List.objects.create()
        response = self.client.get('/lists/%d/' % (correct_list.id,))
        self.assertEqual(response.context['list'], correct_list)

    def test_uses_list_template(self):
        list_ = List.objects.create()
        response = self.client.get('/lists/%d/' % (list_.id,))
        self.assertTemplateUsed(response, 'list.html')

    def test_displays_only_items_for_that_list(self):
        correct_list = List.objects.create()
        Item.objects.create(text='itemey 1', list=correct_list)
        Item.objects.create(text='itemey 2', list=correct_list)
        other_list = List.objects.create()
        Item.objects.create(text='other list item 1', list=other_list)
        Item.objects.create(text='other list item 2', list=other_list)

        response = self.client.get('/lists/%d/' % (correct_list.id,))

        self.assertContains(response, 'itemey 1')
        self.assertContains(response, 'itemey 2')
        self.assertNotContains(response, 'other list item 1')
        self.assertNotContains(response, 'other list item 2')

    def test_can_save_a_POST_request_to_an_existing_list(self):
        correct_list = List.objects.create()
        self.client.post(
            '/lists/%d/' % (correct_list.id,),
            data={'text': 'A new item for an existing list'}
        )
        self.assertEqual(1, Item.objects.count())
        new_item = Item.objects.first()
        self.assertEqual(new_item.text, 'A new item for an existing list')
        self.assertEqual(new_item.list, correct_list)

    def test_POST_redirects_to_list_view(self):
        other_list = List.objects.create()
        correct_list = List.objects.create()

        response = self.client.post(
            '/lists/%d/' % (correct_list.id,),
            {'text': 'A new item for an existing list'}
        )
        new_item = Item.objects.first()
        self.assertRedirects(response, '/lists/%d/' % (correct_list.id,), )

    def post_invalid_input(self):
        list_ = List.objects.create()
        return self.client.post(
            '/lists/%d/' % (list_.id,),
            data={'text': ''}
        )

    def test_for_invalid_input_nothing_saved_to_db(self):
        self.post_invalid_input()
        self.assertEqual(Item.objects.count(), 0)

    def test_for_invalid_input_renders_list_template(self):
        response = self.post_invalid_input()
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'list.html')

    def test_for_invalid_input_passes_form_to_template(self):
        response = self.post_invalid_input()
        self.assertIsInstance(response.context['form'], ExistingListItemForm)

    def test_for_invalid_input_shows_error_on_page(self):
        response = self.post_invalid_input()
        self.assertContains(response, escape(EMPTY_LIST_ERROR))

    def test_duplicate_item_validation_errors_end_up_on_lists_page(self):
        list1 = List.objects.create()
        item1 = Item.objects.create(list=list1, text='textey')
        response = self.client.post(
            '/lists/%d/' % (list1.id,),
            data={'text': 'textey'}
        )
        expected_error = escape(DUPLICATE_ITEM_ERROR)
        self.assertContains(response, expected_error)
        self.assertTemplateUsed(response, 'list.html')
        self.assertEqual(Item.objects.all().count(), 1)

    def test_displays_item_form(self):
        list_ = List.objects.create()
        response = self.client.get('/lists/%d/' % (list_.id,))
        self.assertIsInstance(response.context['form'], ExistingListItemForm)
        self.assertContains(response, 'name="text"')

    def test_displays_sharee_to_owner(self):
        owner = User.objects.create(email="a@b.com")
        list_ = List.create_new('item 1', owner=owner)
        sharee = User.objects.create(email="c@d.com")
        list_.shared_with.add(sharee)
        request = HttpRequest()
        request.user = owner
        response = view_list(request, list_.id)
        self.assertContains(response, 'c@d.com')

    def test_non_owner_cannot_see_sharee(self):
        owner = User.objects.create(email="a@b.com")
        list_ = List.create_new('item 1', owner=owner)
        sharee = User.objects.create(email="c@d.com")
        list_.shared_with.add(sharee)
        request = HttpRequest()
        request.user = sharee
        response = view_list(request, list_.id)
        self.assertContains(response, 'c@d.com')

    def test_sharee_see_sharer(self):
        owner = User.objects.create(email="a@b.com")
        list_ = List.create_new('item 1', owner=owner)
        sharee = User.objects.create(email="c@d.com")
        list_.shared_with.add(sharee)
        request = HttpRequest()
        request.user = sharee
        response = view_list(request, list_.id)
        self.assertContains(response, 'a@b.com')

    def test_see_anonymous_owner(self):
        list_ = List.create_new('item 1')
        response = self.client.get('/lists/%d/' % (list_.id,))
        self.assertContains(response, 'Anonymous User')

    def test_sees_non_anonymous_owner(self):
        owner = User.objects.create(email='a@b.com')
        list_ = List.create_new('item 1', owner=owner)
        response = self.client.get('/lists/%d/' % (list_.id,))
        self.assertContains(response, 'a@b.com')

class HomePageTest(TestCase):

    def test_home_page_renders_home_template(self):
        response = self.client.get('/')
        self.assertTemplateUsed(response, 'home.html')

    def test_home_page_uses_item_form(self):
        response = self.client.get('/')
        self.assertIsInstance(response.context['form'], ItemForm)

class MyListsTest(TestCase):

    def test_my_lists_url_renders_my_lists_template(self):
        response = self.client.get('/lists/users/a@b.com/')
        self.assertTemplateUsed(response, 'my_lists.html')

    def test_passes_correct_owner_to_template(self):
        User.objects.create(email="wrong@owner.com")
        correct_user = User.objects.create(email='a@b.com')
        response = self.client.get('/lists/users/a@b.com/')
        self.assertEqual(response.context['owner'], correct_user)

class ShareListTest(TestCase):

    def test_post_redirects_to_lists_page(self):
        list_ = List.objects.create()
        sharee = User.objects.create(email='a@b.com')
        response = self.client.post(
            '/lists/%d/share' % list_.id,
            data={'email': 'a@b.com'}
        )
        self.assertRedirects(response, '/lists/%d/' % list_.id)

    def test_post_add_email_to_shared_with(self):
        list_ = List.objects.create()
        sharee = User.objects.create(email='a@b.com')
        self.client.post(
            "/lists/%d/share" % list_.id,
            data={'email': sharee.email}
        )
        self.assertIn(
            sharee,
            list_.shared_with.all()
        )