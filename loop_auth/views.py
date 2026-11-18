from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST
from .forms import RegisterForm, LoopAuthenticationForm

def register_view(request):
    if request.user.is_authenticated:
        return redirect("loop_auth:dashboard")
    form = RegisterForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        login(request, user)
        messages.success(request, "Your account has been created.")
        return redirect("loop_auth:dashboard")
    return render(request, "loop_auth/auth.html", {"form": form, "mode": "register"})

def login_view(request):
    if request.user.is_authenticated:
        return redirect("loop_auth:dashboard")
    form = LoopAuthenticationForm(request, data=request.POST or None)
    if request.method == "POST" and form.is_valid():
        login(request, form.get_user())
        return redirect(request.POST.get("next") or "loop_auth:dashboard")
    return render(request, "loop_auth/auth.html", {
        "form": form, "mode": "login", "next": request.GET.get("next", "")
    })

@login_required
def dashboard_view(request):
    return render(request, "loop_auth/dashboard.html")

#@require_POST
@login_required
def logout_view(request):
    logout(request)
    return redirect("loop_auth:login")
