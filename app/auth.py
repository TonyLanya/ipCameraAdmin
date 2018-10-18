from django.contrib.auth import authenticate, logout
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import redirect

@csrf_exempt
def login(request):
    user = authenticate(username='tonylanya', password='tonylanya')
    if user is not None:
        print("authenticated")
        login(request)
        return redirect("/")
        #return redirect(request.POST.get('next'))
    else:
        print("not authenticated")
        return redirect('/login?next=' + request.POST.get('next'))

@csrf_exempt
def logout(request):
    logout(request)
    return redirect('/login')