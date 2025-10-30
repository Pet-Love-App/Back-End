from django.contrib import admin

import additive
from additive.models import Ingredient

# Register your models here.
admin.register(additive, Ingredient)
