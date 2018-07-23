from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views import generic
from django.contrib.auth.models import User
from django.urls import reverse_lazy


@login_required
def home_view(request):
    return redirect(reverse('cases:case_list'))


class UserChangeView(LoginRequiredMixin, UserPassesTestMixin, generic.UpdateView):
    model = User
    fields = ['first_name', 'last_name', 'email']
    template_name = 'registration/user_change.html'
    success_url = reverse_lazy('home')
    raise_exception = True  # from UserPassesTestMixin, raises 403 forbidden if test failed

    def form_valid(self, form):
        form.instance.caseworker.name = form.instance.first_name + ' ' + form.instance.last_name
        form.instance.caseworker.save()
        return super().form_valid(form)

    def test_func(self):
        return self.request.user.id == self.kwargs['pk']
