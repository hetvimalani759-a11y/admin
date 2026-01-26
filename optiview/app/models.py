from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=200)
    price = models.IntegerField()
    image = models.ImageField(upload_to='products/')
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    brand = models.CharField(max_length=100, blank=True)
    shape = models.CharField(max_length=100, blank=True)
    frame_material = models.CharField(max_length=100, blank=True)
    lens_color = models.CharField(max_length=100, blank=True)
    size = models.CharField(max_length=50, blank=True)
    gender = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return self.name
