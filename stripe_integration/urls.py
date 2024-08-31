# urls.py
from django.urls import path

from .views import (
    cancel_subscription,
    cancel_view,
    create_checkout_session,
    get_packages,
    payment_history,
    show_packages,
    success_view,
)

urlpatterns = [
    path("show-packages/", show_packages, name="show_packages"),
    path("success/", success_view, name="success"),
    path("cancel/", cancel_view, name="cancel"),
    path("get-packages/", get_packages, name="get_packages"),
    path(
        "create-checkout-session/",
        create_checkout_session,
        name="create_checkout_session",
    ),
    path("payment-history/", payment_history, name="payment_history"),
    path("cancel_subscription", cancel_subscription, name="cancel_subscription"),
]
