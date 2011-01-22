$(document).ready(function() {
  $(".photo-container").live("hover", function() {
    $(this).children(".edit-menu").fadeToggle(100);
  });
});
