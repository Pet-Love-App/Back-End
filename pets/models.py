# pets/models.py
from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Pet(models.Model):
    """宠物模型"""

    PET_TYPES = [
        ("dog", "狗"),
        ("cat", "猫"),
        ("bird", "鸟"),
        ("fish", "鱼"),
        ("other", "其他"),
    ]

    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="pets")
    name = models.CharField(max_length=100)
    pet_type = models.CharField(max_length=20, choices=PET_TYPES)
    breed = models.CharField(max_length=100, blank=True, null=True)
    birth_date = models.DateField(blank=True, null=True)
    weight = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    color = models.CharField(max_length=50, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    avatar = models.ImageField(upload_to="pet_avatars/", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "pets_pet"
        ordering = ["-created_at"]


class PetHealthRecord(models.Model):
    """宠物健康记录"""

    pet = models.ForeignKey(Pet, on_delete=models.CASCADE, related_name="health_records")
    record_date = models.DateField()
    weight = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    temperature = models.DecimalField(max_digits=4, decimal_places=1, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    vet_name = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "pets_healthrecord"
        ordering = ["-record_date"]


class PetVaccination(models.Model):
    """宠物疫苗记录"""

    pet = models.ForeignKey(Pet, on_delete=models.CASCADE, related_name="vaccinations")
    vaccine_name = models.CharField(max_length=100)
    vaccination_date = models.DateField()
    next_due_date = models.DateField(blank=True, null=True)
    vet_name = models.CharField(max_length=100, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "pets_vaccination"
        ordering = ["-vaccination_date"]
