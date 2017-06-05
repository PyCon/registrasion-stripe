Stripe.setPublishableKey('{{ PINAX_STRIPE_PUBLIC_KEY }}');


$(function() {
  var $form = $('#payment-form');
  $form.submit(function(event) {

    if ($form.find("input[name='stripe_token']").length) {
      // If we've added the stripe token, then we're good to go.
      return true;
    }

    // Disable the submit button to prevent repeated clicks:

    $form.find('input[type=submit]').prop('disabled', true);

    console.log($form.number);

    // Request a token from Stripe:
    Stripe.card.createToken($form, stripeResponseHandler);

    // Prevent the form from being submitted:
    return false;
  });
});

function stripeResponseHandler(status, response) {
  // Grab the form:
  var $form = $('#payment-form');
  var $submit = $form.find('input[type=submit]')
  if (response.error) { // Problem!
    console.log(response.error.message);

    // Show the errors on the form:
    $form.find('#payment-errors').text(response.error.message);
    $form.find('#payment-errors-outer').show();
    $submit.prop('disabled', false); // Re-enable submission

  } else { // Token was created!
    console.log(response);

    // Get the token ID:
    var token = response.id;

    // Insert the token ID into the form so it gets submitted to the server:
    $form = $form.append($('<input type="hidden" name="stripe_token" />').val(token));

    // Submit the form:
    /*
    $form.get(0).submit();
    $form.append($('<p>').text("Processing your payment. Please do not refresh."));
    */
    console.log("boop");
  }
};
