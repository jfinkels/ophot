$(document).ready(function() {
  $("#photosbanner").hide(); // hide the photos banner by default

  // when the photos link is clicked, highlight it and fade in the banner
  $("#photoslink").click(function (event) {
    // prevent the browser from going to the top of the page due to "#" href
    event.preventDefault();

    $("#photoslink").toggleClass("selected");
    /* $("#photosbanner").fadeToggle("fast"); */
    $("#photosbanner").toggle("slide", { direction : "right" }, 500);
  });
});
