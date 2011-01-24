/**
 * Creates the table cell for each photo requested by the displayPhotos()
 * function. The unique ID of the photo is photo_id, which is filled into the
 * "id" attribute of the <img> element, and the path to the file is specified
 * in filename.
 */
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

/**
 * Callback which adds new cells to the <tr> element with id "the-row", each
 * containing the filename specified in data. The data object contains a map
 * from the unique ID of the photo to display to the path to that photo.
 */
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
}

/**
 * Initializes the state of some elements and establishes some event handlers.
 */
$(document).ready(function() {
  $("#contact-info").hide();
  $("#photos-banner").hide();
  $("#photos-container").hide();
  $("#splash-shadow").hide();
  $(".submenu").hide();

  $(".photo-container").live("hover", function() {
    $(this).children(".purchase").toggle();
  });

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
      $("#contact-link").removeClass("selected");
      $(this).addClass("selected");
      $("#contact-info").fadeOut();
      $("#splash-shadow").fadeOut();
      $(".submenu").show();
    }
  });

  $("#contact-link").click(function(event) {
    event.preventDefault();
    if ($(this).hasClass("selected")) {
      $(this).removeClass("selected");
      $("#splash-shadow").fadeOut();
      $("#contact-info").fadeOut();
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
      $("#contact-link").removeClass("selected");
      $(".photo-link").removeClass("selected");
      $(this).addClass("selected");

      $("#contact-info").fadeOut();
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
