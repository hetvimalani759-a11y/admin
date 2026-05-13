import os
import django
import csv

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "optiview.settings")
django.setup()

from app.models import PincodeMapping

with open('pincodes.csv', newline='', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        pincode = row['pincode'].strip()
        area = row['area'].strip()
        city = row['city'].strip()
        state = row['state'].strip()

        obj, created = PincodeMapping.objects.update_or_create(
            pincode=pincode,
            area=area,  # only lookup by pincode
            defaults={ 'city': city, 'state': state}
        )

        if created:
            print(f"✅ Created: {pincode} - {area}")
        else:
            print(f"✔ Already exists: {pincode} - {area}")

print("Import finished!")