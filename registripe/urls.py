from django.conf.urls import url

from registripe import views

from pinax.stripe.views import (
    Webhook,
)


urlpatterns = [
    url(r"^card/([0-9]*)/$", views.card, name="registripe_card"),
    url(r"^card/([0-9]*)/([0-9A-Za-z]*)/$", views.card, name="registripe_card"),
    url(r"^form_handler.js", views.form_handler, name="registripe_form_handler"),
    url(r"^refund/([0-9]*)/$", views.refund, name="registripe_refund"),
    url(r"^webhook/$", Webhook.as_view(), name="pinax_stripe_webhook"),
]
