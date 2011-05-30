$(document).ready(function() {
  $("p#new-category").hide();
  $("select#category").change(function() {
    if ($(this).children(":selected").val() == -1) {
      $("input#new-cat-name").val("");
      $("p#new-category").show();
    } else {
      $("p#new-category:visible").hide();
    }
  });
});