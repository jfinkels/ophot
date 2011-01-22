$(document).ready(function() {
  $(".photo-container").live("mouseover", function(event) {
    $(this).children(".edit-menu").fadeIn();
    $(this).addClass("highlighted");
  });
  $(".photo-container").live("mouseout", function(event) {
    $(this).children(".edit-menu").fadeOut();
    $(this).removeClass("highlighted");
  });
});
