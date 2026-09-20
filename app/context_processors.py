from django.db.models import Sum

from .models import Cart


def cart_count(request):
    # Read-only: never creates a session, so anonymous visitors who have not
    # touched the cart cost nothing.
    session_key = request.session.session_key
    if not session_key:
        return {'cart_count': 0}
    total = Cart.objects.filter(session_key=session_key).aggregate(total=Sum('user_amount'))['total']
    return {'cart_count': total or 0}
