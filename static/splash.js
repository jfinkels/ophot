function displayPhotos(data, textStatus, xhr) {
  for (var i = 0; i < data.photos.length; i++) {
    $("#the-row").append("<td><img src=" + data.photos[i] + " /></td>");
  }
}

$(document).ready(function() {
  $("#contact-info").hide();
  $("#photos-banner").hide();
  $("#photos-container").hide();
  $("#splash-shadow").hide();
  $(".submenu").hide();

  $("#photos-link").click(function(event) {
    event.preventDefault();
    if ($(this).hasClass("selected")) {
      $(this).removeClass("selected");
      $(".submenu").hide();
      $("#photos-container").fadeOut();
      $("#banner-container").animate({ top : 400 }, 500);
      $("#splash-shadow").fadeOut();
    } else {
      $(this).addClass("selected");
      $(".submenu").show();
    }
  });

  $("#contact-link").click(function(event) {
    event.preventDefault();
    if ($(this).hasClass("selected")) {
      $("#splash-shadow").fadeOut();
      $("#contact-info").fadeOut();
      $(this).removeClass("selected");
    } else {
      $("#photos-link").removeClass("selected")
      $(".photo-link").each(function() {
        $(this).removeClass("selected");
      });
      $(".submenu").hide();
      $("#photos-container").fadeOut();
      $("#banner-container").animate({ top : 400 }, 500);
      $("#splash-shadow").fadeIn();
      $("#contact-info").fadeIn();
      $(this).addClass("selected");
    }
  });

  $(".photo-link").click(function(event) {
    event.preventDefault();
    if (!$(this).hasClass("selected")) {
      $("#contact-info").fadeOut();
      $("#contact-link").removeClass("selected");
      $("#banner-container").animate({ top : 450 }, 500);
      $("#splash-shadow").fadeIn();
      $(".photo-link").each(function() {
        $(this).removeClass("selected");
      });
      $(this).addClass("selected");
      $("#photos-container").fadeIn();
      $("#the-row").empty();
      var category = $(this).attr("id");
      $.getJSON(SCRIPT_ROOT + '/_get_photos', {category : category},
                displayPhotos);
    }
  });
});
