function createPhotoCellString(photo_id, filename) {
  return "<td class=\"photo-cell\">\n"
       + "  <div class=\"photo-container\">\n"
       + "    <a class=\"purchase\" href=\"#\">purchase</a>\n"
       + "    <div class=\"photo-shadow\"></div>\n"
       + "    <div class=\"confirm-delete\">\n"
       + "      <p>Are you sure you want to delete this photo?</p>\n"
       + "      <p class=\"choice\">\n"
       + "        <a href=\"#\" class=\"cancel\">Cancel</a>\n"
       + "        <a href=\"#\" class=\"confirm\">Delete</a>\n"
       + "      </p>\n"
       + "    </div>\n"
       + "    <a href=\"#\" class=\"delete\">delete</a>\n"
       + "    <img src=" + filename + " id=\"" + photo_id + "\"/>\n"
       + "  </div>\n"
       + "</td>\n";
}

function displayPhotos(data, textStatus, xhr) {
  // assume the data is an associative array mapping display positions to
  // filenames
  var index = 0;
  for (var id in data) {
    $("#the-row").append(createPhotoCellString(id, data[id]));
  }

  // hide these things as soon as they are created
  $(".delete").hide();
  $(".purchase").hide();
  $(".photo-shadow").hide();
  $(".confirm-delete").hide();

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

  $(".photo-container").live("hover", function() {
    $(this).children(".purchase").toggle();
  });

  // TODO do this instead of what i'm doing: http://docs.jquery.com/Frequently_Asked_Questions#How_do_I_determine_the_state_of_a_toggled_element.3F
  // TODO also use .siblings()
  // TODO use callbacks to make things animate in sequence instead of simult.
  // TODO decompose these long functions into smaller reusable ones
  $("#photos-link").click(function(event) {
    event.preventDefault();
    if ($(this).hasClass("selected")) {
      $(this).removeClass("selected");
      $(".photo-link").removeClass("selected");
      $(".submenu").hide(0, function() {
        $("#photos-container").fadeOut();
        $("#splash-shadow").fadeOut(400, function() {
          $("#banner-container").animate({ top : 400 }, 500);
        });
      });
    } else {
      $("#contact-info").fadeOut();
      $("#contact-link").removeClass("selected");
      $("#splash-shadow").fadeOut();
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
      $(".photo-link").removeClass("selected");
      $(this).addClass("selected");

      $(".submenu").hide();
      $("#splash-shadow").fadeIn();

      if ($("#photos-container").is(":visible")) {
        $("#photos-container").fadeOut(400, function() {
          $("#banner-container").animate(
            { top : 400 }, 
            {
              duration: 500,
              complete: function() {
                $("#contact-info").fadeIn();
              }
            });
        });
      } else {
        $("#contact-info").fadeIn();        
      }
    }
  });

  $(".photo-link").click(function(event) {
    event.preventDefault();
    if (!$(this).hasClass("selected")) {
      $("#contact-info").fadeOut();
      $("#contact-link").removeClass("selected");
      $(".photo-link").removeClass("selected");
      $(this).addClass("selected");

      if ($("#photos-container").is(":hidden")) {
        $("#banner-container").animate(
          { top : 497 },
          {
            duration: 500,
            complete: function() {
              $("#splash-shadow").fadeIn();
              $("#photos-container").fadeIn();
            }
          });
      }

      $("#the-row").empty();
      var category = $(this).attr("id");
      $.getJSON(SCRIPT_ROOT + '/_get_photos', {category : category},
                displayPhotos);
    }
  });
});
