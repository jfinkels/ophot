$(document).ready(function() {
  $("a.close").click(function(event) {
    event.preventDefault();
    $(this).parent().hide("fade", 200);
  });
});
