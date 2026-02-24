from django.db import models

class Order(models.Model):
    delivery_person = models.ForeignKey(
    "delivery.DeliveryPerson",
    on_delete=models.SET_NULL,
    null=True,
    blank=True,
    related_name="orders"
)


    items = models.TextField()
    status = models.CharField(max_length=50)

    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    created_at = models.DateTimeField(auto_now_add=True)

