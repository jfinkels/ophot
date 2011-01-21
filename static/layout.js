$(document).ready(function() {
  $("a.close").click(function () {
    $(this).parent(".flash").hide("fade", 200);
  });
});
