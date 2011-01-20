$(document).ready(function() {
  $("a.close").click(function () {
    $(this).parent(".flash").fadeOut("slow");
  });
});
