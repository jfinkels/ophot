$(document).ready(function() {
  // hide these elements by default
  $("#photosbanner").hide();
  $("#splash-shadow").hide();
  $("#contact-info").hide();

  // when the photos link is clicked, highlight it and fade in the banner
  $("#photoslink").click(function (event) {
    // prevent the browser from going to the top of the page due to "#" href
    event.preventDefault();

    $("#photoslink").toggleClass("selected");
    /* $("#photosbanner").fadeToggle("fast"); */
    $("#photosbanner").toggle("slide", { direction : "right" }, 500);
  });

  // when the contact link is clickec, highlight it, shadow the splash photo,
  // and open the contact information
  $("#contact-link").click(function (event) {
    // prevent the browser from going to the top of the page due to "#" href
    event.preventDefault();

    $("#contact-link").toggleClass("selected");
    $("#splash-shadow").fadeToggle();
    $("#contact-info").fadeToggle();
  });
});
