from django.shortcuts import render



def index(request):
    return render(request, 'chat/index.html')

def test(request):
    return render(request, 'chat/test.html')
