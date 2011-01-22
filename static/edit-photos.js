$(document).ready(function() {
  $(".photo-container").live("mouseover", function(event) {
    $(this).children(".edit-menu").show();
    $(this).addClass("highlighted");
  });
  $(".photo-container").live("mouseout", function(event) {
    $(this).children(".edit-menu").hide();
    $(this).removeClass("highlighted");
  });
});
