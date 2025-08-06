from django.shortcuts import render, redirect, get_object_or_404
from django.utils.crypto import get_random_string

from .forms import LoginForm
from .models import Challenge


def login(request):
    if request.method == "POST":
        form = LoginForm(request.POST)

        if form.is_valid():
            chal = form.save(commit=False)
            chal.challenge_domain = (f"{get_random_string(length=32).lower()}"
                                     f"-awd.{chal.domain}")
            chal.key = get_random_string(length=255)
            chal.save()
            request.session["chal"] = chal.key

            context = {
                "chal": chal,
            }

            return render(request, "authly/challenge.html", context)
        else:
            context = {
                "form": form,
            }

            return render(request, "authly/login.html", context)
    else:
        form = LoginForm()

        context = {
            "form": form,
        }

        return render(request, "authly/login.html", context)


def verify(request):
    try:
        chal = Challenge.objects.get(key=request.session["chal"])
    except (KeyError, Challenge.DoesNotExist):
        return redirect("authly:login")

    if chal.check_ct():
        return redirect("home:home")
    else:
        return redirect("authly:login")


def logout(request):
    try:
        chal = Challenge.objects.get(key=request.session["chal"])
    except (KeyError, Challenge.DoesNotExist):
        return redirect("authly:login")

    if request.method == "POST":
        chal.delete()
        request.session["chal"] = ""
        return redirect("authly:login")
    else:
        context = {
            "chal": chal,
        }

        return render(request, "authly/logout.html", context)
