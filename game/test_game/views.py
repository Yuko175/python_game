from django.shortcuts import render
from django.views import View
import datetime
from .forms import MyForm

class IndexView(View):
    def get(self, request):
        now = datetime.datetime.now()
        return render(request, 'test_game/index.html', {'now': now, 'form': MyForm()})
    def post(self, request):
        form = MyForm(request.POST)
        if form.is_valid() and form.cleaned_data['age'] >= 0:
            print(form.cleaned_data)
            form.save()
            return render(request, 'test_game/index.html', {'form': MyForm()})
        return render(request, '', {'form': form})

index = IndexView.as_view()
