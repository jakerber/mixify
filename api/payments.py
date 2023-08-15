"""Stripe API wrapper module."""
import config
import stripe

stripe.api_key = config.STRIPE_SECRET_KEY


def create_boost_payment() -> str:
    """Create a Stripe payment intent for Mixify boost.

    :return: intent client secret
    """
    intent = stripe.PaymentIntent.create(
        amount=99,
        currency='usd',
        automatic_payment_methods={'enabled': True},
        description='Mixify Boost',
        statement_descriptor='Mixify Boost')
    return intent.client_secret
