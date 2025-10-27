from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.db import transaction

from .forms import TravelRequestForm, ExpenseItemFormSet
from .models import TravelRequest


@login_required
def rka_new(request):
    if request.method == "POST":
        form = TravelRequestForm(request=request, data=request.POST)
        if form.is_valid():
            tr = form.save(commit=False)
            tr.applicant = request.user
            tr.save()
            messages.success(request, "Reisekostenantrag gespeichert.")
            return redirect("rka_list")
    else:
        form = TravelRequestForm(request=request)
    return render(request, "rka/edit.html", {"form": form, "mode": "new"})
@login_required
@transaction.atomic
def rka_edit(request, pk):
    tr = get_object_or_404(TravelRequest, pk=pk, applicant=request.user)
    if request.method == "POST":
        form = TravelRequestForm(request.POST, request.FILES, instance=tr)
        formset = ExpenseItemFormSet(request.POST, request.FILES, instance=tr)
        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
            return redirect(reverse("rka_list"))
    else:
        form = TravelRequestForm(instance=tr)
        formset = ExpenseItemFormSet(instance=tr)
    return render(
        request,
        "rka/edit.html",
        {"form": form, "formset": formset, "mode": "edit", "tr": tr},
    )


@login_required
def rka_list(request):
    qs = (TravelRequest.objects
          .select_related("applicant")
          .order_by("-created_at"))
    return render(request, "rka/list.html", {"requests": qs})
