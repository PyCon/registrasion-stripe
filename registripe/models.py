from __future__ import unicode_literals

from django.db import models
from registrasion.models import commerce
from pinax.stripe.models import Charge


class StripePayment(commerce.PaymentBase):

    charge = models.ForeignKey(Charge, on_delete=models.CASCADE)

class StripeCreditNoteRefund(commerce.CreditNoteRefund):

    charge = models.ForeignKey(Charge, on_delete=models.CASCADE)
