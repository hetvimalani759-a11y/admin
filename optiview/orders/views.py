from django.shortcuts import render, get_object_or_404, redirect
from .models import Order
from .forms import OrderAssignForm

def assign_order(request, order_id):

    order = get_object_or_404(Order, id=order_id)

    if request.method == "POST":
        form = OrderAssignForm(request.POST, instance=order)
        if form.is_valid():
            form.save()
            return redirect("admin_dashboard")
    else:
        form = OrderAssignForm(instance=order)

    return render(request, "admin_panel/assign_order.html", {
        "form": form,
        "order": order
    })