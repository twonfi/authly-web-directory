from django.shortcuts import render, redirect
from django.utils.crypto import get_random_string
from django.contrib.auth.hashers import make_password, check_password

from .forms import LoginForm
from .models import Challenge


def login(request):
    if request.method == "POST":
        form = LoginForm(request.POST)

        if form.is_valid():
            chal = form.save(commit=False)
            chal.challenge_domain = (f"{get_random_string(length=32).lower()}"
                                     f"-awd.{chal.domain}")
            request.session["chal"] = get_random_string(length=255)
            chal.key = make_password(request.session["chal"])
            chal.save()
            request.session["domain"] = chal.challenge_domain

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
        chal = Challenge.objects.get(
            challenge_domain=request.session["domain"])
    except (KeyError, Challenge.DoesNotExist):
        return redirect("authly:login")

    if not check_password(request.session["chal"], chal.key):
        return redirect("authly:login")

    if check_password(request.session["chal"], chal.key) and chal.check_ct():
        return redirect("directory:site_list")
    else:
        return redirect("authly:login")


def logout(request):
    try:
        chal = Challenge.objects.get(
            challenge_domain=request.session["domain"])
    except (KeyError, Challenge.DoesNotExist):
        return redirect("authly:login")

    if not check_password(request.session["chal"], chal.key):
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
