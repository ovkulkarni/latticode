from django.core.files.uploadedfile import InMemoryUploadedFile
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.views import LoginView as AuthLoginView, LogoutView as AuthLogoutView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.urls import reverse

import tempfile

from .forms import GameForm
from .models import Game


class RegistrationView(View):
    template_name = 'users/register.html'
    form = UserCreationForm

    def post(self, request, *args, **kwargs):
        form = self.form(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Successfully registered!")
            return redirect('login')
        return render(request, self.template_name, {'form': form})

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, {'form': self.form()})


class LoginView(AuthLoginView):
    template_name = 'users/login.html'


class LogoutView(AuthLogoutView):
    template_name = 'users/logout.html'


class IndexView(View):
    def get(self, request, *args, **kwargs):
        context = {}
        if request.user.is_authenticated:
            context['games'] = Game.objects.filter(user=request.user)
        return render(request, 'index.html', context)


class GameView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        game_model = get_object_or_404(Game, pk=kwargs.pop('id'))
        content = game_model.code.read().decode()
        return render(request, 'create.html', {'game_model': game_model, 'inp': content})

    def post(self, request, *args, **kwargs):
        game_model = get_object_or_404(Game, pk=kwargs.pop('id'))
        tmp = tempfile.NamedTemporaryFile()
        tmp.write(request.POST['code_input'].encode())
        request.FILES['code'] = InMemoryUploadedFile(
            tmp, 'code', 'textInputFile', 'text/x-python-script',
            len(request.POST['code_input']),
            'utf-8')
        form = GameForm(request.POST, request.FILES, instance=game_model)
        game_model = form.save(commit=False)
        game_model.user = request.user
        game_model.save()
        return redirect(reverse('view_game', kwargs={'id': game_model.pk}))


class PlayView(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'create.html', {'hide_editor': True, 'room_id': kwargs.pop('room_id')})


class CreateView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        return render(request, 'create.html', {})

    def post(self, request, *args, **kwargs):
        tmp = tempfile.NamedTemporaryFile()
        tmp.write(request.POST['code_input'].encode())
        request.FILES['code'] = InMemoryUploadedFile(
            tmp, 'code', 'textInputFile', 'text/x-python-script',
            len(request.POST['code_input']),
            'utf-8')
        form = GameForm(request.POST, request.FILES)
        if form.is_valid():
            game_model = form.save(commit=False)
            game_model.user = request.user
            game_model.save()
            return redirect(reverse('view_game', kwargs={'id': game_model.pk}))
        else:
            return render(request, 'create.html', {'inp': request.POST['code_input']})
