function displayPhotos(data, textStatus, xhr) {
    alert(data.photos);
  for (var i = 0; i < data.photos.length; i++) {
    $("#the-row").append(
        "<td>\n"
      + "  <div class=\"photo-container\">\n"
      + "    <div class=\"photo-shadow\"></div>\n"
      + "    <div class=\"edit-menu\" id=\"edit-menu-" + i + "\">\n"
      //+ "      <span class=\"drag\">drag to move</span>\n"
      + "      <a href=\"#\" class=\"delete\">delete</a>\n"
      + "    </div>\n"
      + "    <img src=" + data.photos[i] + " id=\"" + data + "\"/>\n"
      + "  </div>\n"
      + "</td>\n");
    // hide the edit menu as soon as it is created!
    $("#edit-menu-" + i).hide();
  }
  // TODO sortable does not seem to work very well
  // $("#the-row").sortable({ axis: 'x',
  //                          opacity: 0.8,
  //                          placeholder: 'placeholder',
  //                          forcePlaceholderSize: true });
  // $("#the-row").disableSelection();
}

$(document).ready(function() {
  $("#contact-info").hide();
  $("#photos-banner").hide();
  $("#photos-container").hide();
  $("#splash-shadow").hide();
  $(".submenu").hide();

  // TODO do this instead of what i'm doing: http://docs.jquery.com/Frequently_Asked_Questions#How_do_I_determine_the_state_of_a_toggled_element.3F
  // TODO also use .siblings()
  $("#photos-link").click(function(event) {
    event.preventDefault();
    if ($(this).hasClass("selected")) {
      $(this).removeClass("selected");
      $(".submenu").hide();
      $("#photos-container").fadeOut();
      $("#banner-container").animate({ top : 400 }, 500);
      $("#splash-shadow").fadeOut();
      $(".photo-link").each(function() {
        $(this).removeClass("selected");
      });
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
      $("#banner-container").animate({ top : 497 }, 500);
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
