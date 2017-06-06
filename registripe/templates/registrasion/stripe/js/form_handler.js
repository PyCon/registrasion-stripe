var stripe = Stripe('pk_test_LoicxDzylNLLfsL8Thk1NFTZ');
var elements = stripe.elements();

function makeIntoTextField(element) {
  element.setAttribute("class", "form-control");
}
