from ninja import Router
from .models import Question

router = Router()

@router.get('/')
def say_hello(request):
    return f"Hello"