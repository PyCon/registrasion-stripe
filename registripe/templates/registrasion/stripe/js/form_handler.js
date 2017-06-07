var stripe = Stripe('{{ PINAX_STRIPE_PUBLIC_KEY }}');
var elements = stripe.elements();

function stripeify(elementId) {
  var element = elements.create(elementId);
  element.mount('#' + elementId);

  var htmlElement = document.getElementById(elementId);
  var errors = elementId + "-errors";
  htmlElement.insertAdjacentHTML("afterend", "<div id='" + errors + "' role='alert' class='help-block'></div>");
  var displayError = document.getElementById(errors);

  //Handle real-time validation errors from the card Element.
  element.addEventListener('change', function(event) {
    toggleErrorMessage(displayError, event.error);
  });

  // Create a token or display an error when the form is submitted.
  var paymentForm = document.getElementById('payment-form');
  paymentForm.addEventListener('submit', function(event) {
    event.preventDefault();

    stripe.createToken(element).then(function(result) {
      if (result.error) {
        // Inform the user if there was an error
        toggleErrorMessage(displayError, result.error);
      } else {
        // Send the token to your server
        stripeTokenHandler(result.token);
      }
    });
  });
}

function toggleErrorMessage(errorElement, maybeError) {
  errorClass = inputErrorClassName();
  if (maybeError) {
    errorElement.textContent = maybeError.message;
    errorElement.parentNode.classList.add(errorClass);
  } else {
    errorElement.textContent = '';
    errorElement.parentNode.classList.remove(errorClass);
  }
}


function inputErrorClassName() {
  return {% block form_control_error_class %}"has-error"{% endblock %};
}


function stripeTokenHandler(token) {
  // Insert the token ID into the form so it gets submitted to the server

  var form = document.getElementById('payment-form');
  tokenHolder = form.getElementsByClassName('registrasion-stripe-token')[0];
  inputId = tokenHolder.dataset.inputId;

  var hiddenInput = document.createElement('input');
  hiddenInput.setAttribute('type', 'hidden');
  hiddenInput.setAttribute('name', inputId);
  hiddenInput.setAttribute('value', token.id);

  tokenHolder.appendChild(hiddenInput);

  // Submit the form
  form.submit();
}
