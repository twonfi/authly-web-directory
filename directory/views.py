from django.shortcuts import render, redirect
from django.http import Http404

from .models import Website, Review
from .forms import ManageWebsiteForm, PostReviewForm
from authly.models import Challenge


def site_list(request):
    context = {
        "websites": Website.objects.all().order_by("-last_updated"),
    }

    return render(request, "directory/site_list.html", context)


def site_page(request, domain):
    chal = None
    if request.session["chal"]:
        try:
            chal = Challenge.objects.get(key=request.session["chal"])
        except Challenge.DoesNotExist:
            pass
        else:
            if not chal.check_ct():
                chal = None

    try:
        site = Website.objects.get(domain=domain)
    except Website.DoesNotExist:
        if chal:
            return redirect("directory:manage_site")
        else:
            raise Http404
    else:
        f = PostReviewForm(request.POST or None)

        if request.method == "POST" and f.is_valid():
            r = f.save(commit=False)
            r.site = site
            r.save()

    context = {
        "site": site,
        "chal": chal,
        "f": f,
        "reviews": Review.objects.all().order_by("-id"),
    }

    return render(request, "directory/site_page.html", context)


def manage_website(request):
    if request.session["chal"]:
        try:
            chal = Challenge.objects.get(key=request.session["chal"])
        except Challenge.DoesNotExist:
            pass
        else:
            if chal.check_ct():
                site = Website.objects.get_or_create(domain=chal.domain,
                    defaults={"name": chal.domain})[0]
                f = ManageWebsiteForm(request.POST or None, instance=site)
                if request.method == "POST":
                    if f.is_valid():
                        f.save()
                        return redirect("directory:site_page",
                            domain=site.domain)

                context = {
                    "form": f,
                }

                return render(request,
                    "directory/manage_website.html", context)

    return redirect("authly:login")
