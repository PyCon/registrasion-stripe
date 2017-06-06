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


class NoRenderWidget(forms.widgets.HiddenInput):

    def render(self, name, value, attrs=None):
        return "<!-- no widget: " + name + " -->"


class StripeCardElement(forms.widgets.TextInput):

    def render(self, name, value, attrs=None):
        element = '''
            <div class="registrasion-stripe-element" id='%s' style='"-moz-appearance: textfield; -webkit-appearance: textfield;     appearance: field;"'>Please wait.</div>''' % (name, )

        script = '''<script type='text/javascript'>
            window.addEventListener('load', function(event){
            %s_element = elements.create('card');
            %s_element.mount('#%s');
            });
        </script>''' % (name, name, name)
        return element + script


def secure_striped(field):
    ''' Calls stripe() with secure=True. '''
    return striped(field, True)


def striped(field, secure=False):

    oldwidget = field.widget
    field.widget = StripeWidgetProxy(oldwidget, secure)
    return field


class StripeWidgetProxy(widgets.Widget):

    def __init__(self, underlying, secure=False):
        self.underlying = underlying
        self.secure = secure

    def __deepcopy__(self, memo):
        copy_underlying = copy.deepcopy(self.underlying, memo)
        return type(self)(copy_underlying, self.secure)

    def __getattribute__(self, attr):
        spr = super(StripeWidgetProxy, self).__getattribute__
        if attr in ("underlying", "render", "secure", "__deepcopy__"):
            return spr(attr)
        else:
            return getattr(self.underlying, attr)

    def render(self, name, value, attrs=None):

        if not attrs:
            attrs = {}

        attrs["data-stripe"] = name

        if self.secure:
            name = ""

        return self.underlying.render(name, value, attrs=attrs)


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
        widget=NoRenderWidget(),
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
