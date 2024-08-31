import json
from datetime import datetime

import stripe
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse

# views.py
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

stripe.api_key = settings.STRIPE_SECRET_KEY


@login_required
def show_packages(request):
    STRIPE_PUBLISHABLE_KEY = settings.STRIPE_PUBLISHABLE_KEY
    return render(
        request,
        "stripe_integration/show_packages.html",
        context={"STRIPE_PUBLISHABLE_KEY": STRIPE_PUBLISHABLE_KEY},
    )


def success_view(request):
    session_id = request.GET.get("session_id") or None
    payment_history_url = reverse("payment_history")
    html_content = f"""
    <html>
        <body>
            <h1>Payment successful!</h1>
            <p>Session ID is {session_id}</p>
            <a href="{payment_history_url}">
                <button>View Payment History</button>
            </a>
        </body>
    </html>
    """
    return HttpResponse(html_content)


def cancel_view(request):
    return HttpResponse("Payment canceled.")


@csrf_exempt
def get_packages(request):
    prices = stripe.Price.list(active=True)
    return JsonResponse(prices)


@csrf_exempt
@require_POST
def create_checkout_session(request):
    data = json.loads(request.body)
    price_id = data.get("price_id")
    # Get the domain name dynamically from the request
    domain = request.build_absolute_uri("/")[:-1]
    try:
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[
                {
                    "price": price_id,
                    "quantity": 1,
                }
            ],
            mode="subscription",
            success_url=f"{domain}/stripe/success?session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=f"{domain}/stripe/cancel",
        )
        return JsonResponse({"id": checkout_session.id})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)


@login_required
def payment_history(request):
    user_email = request.user.email

    # Retrieve all customers from Stripe using the email
    customers = stripe.Customer.list(email=user_email).data

    if not customers:
        return render(
            request,
            "stripe_integration/payment_history.html",
            {"error": "No customer found for this email."},
        )

    all_charges = []
    most_recent_subscription = None
    last_payment = None

    # Retrieve charges and subscriptions for each customer ID
    for customer in customers:
        customer_id = customer.id

        # Retrieve the charges for the customer with pagination
        has_more = True
        starting_after = None

        while has_more:
            response = stripe.Charge.list(
                customer=customer_id, limit=100, starting_after=starting_after
            )
            all_charges.extend(response.data)
            has_more = response.has_more
            if has_more:
                starting_after = response.data[-1].id

        # Retrieve the most recent subscription for the customer
        subscriptions = stripe.Subscription.list(customer=customer_id, limit=1).data
        if subscriptions:
            most_recent_subscription = subscriptions[0]

    payment_history = [
        {
            "amount": charge.amount / 100,
            "currency": charge.currency,
            "description": charge.description,
            "status": charge.status,
            "created": datetime.fromtimestamp(charge.created),
        }
        for charge in all_charges
    ]

    if payment_history:
        last_payment = payment_history[0]

    subscription_status = None
    if most_recent_subscription:
        subscription_status = {
            "id": most_recent_subscription.id,
            "status": most_recent_subscription.status,
            "current_period_start": datetime.fromtimestamp(
                most_recent_subscription.current_period_start
            ),
            "current_period_end": datetime.fromtimestamp(
                most_recent_subscription.current_period_end
            ),
        }

    return render(
        request,
        "stripe_integration/payment_history.html",
        {
            "payment_history": payment_history,
            "subscription_status": subscription_status,
            "last_payment": last_payment,
        },
    )


@csrf_exempt
@require_POST
@login_required
def cancel_subscription(request):
    data = json.loads(request.body)
    subscription_id = data.get("subscription_id")

    try:
        # Cancel the subscription
        stripe.Subscription.delete(subscription_id)
        return JsonResponse({"message": "Subscription cancelled successfully."})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)
