Stripe.setPublishableKey('{{ PINAX_STRIPE_PUBLIC_KEY }}');


document.addEventListener("DOMContentLoaded", function(contentLoadedEvent) {
  console.log('DOMContentLoaded');

  var form = document.getElementById("payment-form");
  console.log(form);

  form.addEventListener("submit", function(event) {

    if (form.elements["stripe_token"]) {
      // If we've added the stripe token, then we're good to go.
      return true;
    }

    // Prevent the form from being submitted:
    event.preventDefault();

    // Disable the submit button to prevent repeated clicks:
    form.querySelector('input[type=submit]').disabled = true;

    // Request a token from Stripe:
    Stripe.card.createToken(form, stripeResponseHandler);

    return false;
  });

});

function stripeResponseHandler(status, response) {
  // Grab the form:
  var form = document.getElementById("payment-form");

  if (response.error) { // Problem!
    console.log(response.error.message);
    errorsTextId = "XXXX123-payment-errors-text";

    // Show the errors on the form:
    errorsDiv = document.getElementById('payment-errors');
    errorsText = document.getElementById(errorsTextId);
    if (errorsText) {
      errorsText.remove();
    }
    errorsText = document.createElement("span");
    errorsText.id=errorsTextId;
    errorsDiv.insertAdjacentElement("beforeend", errorsText);
    errorsText.insertAdjacentText("afterbegin", response.error.message);
    errorsDiv.style = "";
    errorsDiv.hidden = false;

    // Re-enable submission
    form.querySelector('input[type=submit]').disabled = false;

  } else { // Token was created!
    console.log(response);

    // Get the token ID:
    var token = response.id;

    // Insert the token ID into the form so it gets submitted to the server:
    stripeTokenElement = document.createElement("input");
    stripeTokenElement.setAttribute("type", "hidden");
    stripeTokenElement.setAttribute("name", "stripe_token");
    stripeTokenElement.setAttribute("value", token);

    form.insertAdjacentElement("beforeend", stripeTokenElement);

    // Submit the form:
    form.submit();
    form.insertAdjacentHTML("afterend", "<p>Processing your payment. Please do not refresh.</p>");

  }
};
