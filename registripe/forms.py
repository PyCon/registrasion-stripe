import copy
import functools
import models

from django import forms
from django.core.urlresolvers import reverse
from django.core.exceptions import ValidationError
from django.db.models import F, Q
from django.forms import widgets
from django.utils import timezone

from django_countries import countries
from django_countries.fields import LazyTypedChoiceField
from django_countries.widgets import CountrySelectWidget

from pinax.stripe import models as pinax_stripe_models


class StripeCardElement(forms.widgets.TextInput):

    def render(self, name, value, attrs=None):
        element = '''
            <div class="registrasion-stripe-element" id='%s' style='"-moz-appearance: textfield; -webkit-appearance: textfield;     appearance: field;"'>Please wait.</div>''' % (name, )

        script = '''
            <script type='text/javascript'>
                window.addEventListener('load', function(event){
                    stripeify('%s');
                });
            </script>''' % (name)
        return element + script


class StripeTokenWidget(forms.widgets.HiddenInput):

    def render(self, name, value, attrs=None):

        return '''
            <div class='registrasion-stripe-token' style='display:none;'
            data-input-id='%s'
            ></div>
        ''' % (name, )


class CreditCardForm(forms.Form):

    def _media(self):
        js = (
            'https://js.stripe.com/v3/',
            reverse("registripe_form_handler"),
        )

        return forms.Media(js=js)

    media = property(_media)

    card = forms.CharField(
        required=False,
        label="Credit card",
        max_length=255,
        widget=StripeCardElement()
    )

    stripe_token = forms.CharField(
        max_length=255,
        #required=True,
        widget=StripeTokenWidget(),
    )


class TuokcehcForm(forms.Form):

    stripe_token = forms.CharField(
        max_length=255,
        #required=True,
        widget=forms.HiddenInput(),
    )



class StripeRefundForm(forms.Form):

    def __init__(self, *args, **kwargs):
        '''

        Arguments:
            user (User): The user whose charges we should filter to.
            min_value (Decimal): The minimum value of the charges we should
                show (currently, credit notes can only be cashed out in full.)

        '''
        user = kwargs.pop('user', None)
        min_value = kwargs.pop('min_value', None)
        super(StripeRefundForm, self).__init__(*args, **kwargs)

        payment_field = self.fields['payment']
        qs = payment_field.queryset

        if user:
            qs = qs.filter(
                charge__customer__user=user,
            )

        if min_value is not None:
            # amount >= amount_to_refund + amount_refunded
            # No refunds yet
            q1 = (
                Q(charge__amount_refunded__isnull=True) &
                Q(charge__amount__gte=min_value)
            )
            # There are some refunds
            q2 = (
                Q(charge__amount_refunded__isnull=False) &
                Q(charge__amount__gte=(
                    F("charge__amount_refunded") + min_value)
                )
            )
            qs = qs.filter(q1 | q2)

        payment_field.queryset = qs

    payment = forms.ModelChoiceField(
        required=True,
        queryset=models.StripePayment.objects.all(),
    )
