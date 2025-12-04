from django.contrib.auth import get_user_model
from .services import compute_user_reputation

User = get_user_model()

def recompute_user_reputation(user: User):
    compute_user_reputation(user)