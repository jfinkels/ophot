/**
 * This object can store global variables so that we can transfer data between
 * different AJAX callbacks.
 */
// TODO is there a way to do this without globals?
var globalVariables = {};

/**
 * Stores the categories received from the server on the globalVariables
 * object.
 */
function storeCategories(data, textStatus, xhr) {
  globalVariables.categories = new Array();
  var i = 0;
  for (var j in data) {
    globalVariables.categories[i] = data[j];
    i++;
  }
}

/**
 * Creates the table cell for each photo requested by the displayPhotos()
 * function. The unique ID of the photo is *photoid*, which is filled into the
 * "id" attribute of the <img> element, and the path to the file containing the
 * photo is specified in *filename*. *categories* is an array containing the
 * names of the categories to which a photo can be assigned.
 */
function createPhotoCellString(photoid, filename, categories) {
  /*  var options = "";

  for (var i in categories) {
    options += "          <option value=\"" + categories[i] + "\"></option>\n";
  }*/
  // TODO move the logged in specific things out to edit-photo.js
  return "<td class=\"photo-cell\">\n"
       + "  <div class=\"photo-container\">\n"
       + "    <a class=\"purchase\" href=\"#\">purchase</a>\n"
       + "    <div class=\"photo-shadow\"></div>\n"
       + "    <div class=\"move-left\"><a href=\"#\">&larr;</a></div>\n"
       + "    <div class=\"move-right\"><a href=\"#\">&rarr;</a></div>\n"
       + "    <div class=\"purchase-information\">\n"
       + "      <a class=\"close\">X</a>\n"
       + "      <p>\n"
       + "        For pricing or to order prints email\n"
       + "        mike@mikefinkphotography.com\n"
       + "      </p>\n"
       + "    </div>\n"
       + "    <div class=\"delete-dialog\">\n"
       + "      <p>Are you sure you want to delete this photo?</p>\n"
       + "      <p class=\"choice\">\n"
       + "        <a href=\"#\" class=\"cancel\">Cancel</a>\n"
       + "        <a href=\"#\" class=\"confirm-delete\">Delete</a>\n"
       + "      </p>\n"
       + "    </div>\n"
       + "    <div class=\"cat-chooser\">\n"
       + "      <p>Change category to:</p>\n"
       + "      <ul class=\"category-list\"><li></li></ul>\n"
       + "      <p class=\"choice\">\n"
       + "        <a href=\"#\" class=\"cancel\">Cancel</a>\n"
       + "        <a href=\"#\" class=\"confirm-cat-change\">Save</a>\n"
       + "      </p>\n"
       + "    </div>\n"
       + "    <ul class=\"edit-menu\">\n"
       + "      <li>\n"
       + "        <a href=\"#\" class=\"change-cat\">change category</a>\n"
      /*+ "        <select name=\"new-category\" class=\"new-category\">\n"
       + options
       + "        </select>\n"*/
       + "      </li>\n"
       + "      <li><a href=\"#\" class=\"delete\">delete</a></li>\n"
       + "    </ul>\n"
       + "    <img src=" + filename + " id=\"" + photoid + "\"/>\n"
       + "  </div>\n"
       + "</td>\n";
}

/**
 * Callback which adds new cells to the <tr> element with id "the-row", each
 * containing the filename specified in data. The data object contains a map
 * from the unique ID of the photo to display to the path to that photo.
 */
function displayPhotos(data, textStatus, xhr) {

  // get the known categories and store them in the global variable
  // TODO this really only needs to happen once
  $.getJSON(SCRIPT_ROOT + '/_get_categories', storeCategories);

  // assume the data is in the format described in the documentation for the
  // _get_photos route
  var photos = data['values'];
  for (var i = 0; i < photos.length; ++i) {
    $("#the-row").append(createPhotoCellString(photos[i].photoid,
                                               photos[i].filename,
                                               globalVariables.categories));
  }

  // hide these things as soon as they are created
  $(".edit-menu").hide();
  $(".cat-chooser").hide();
  $(".purchase").hide();
  $(".photo-shadow").hide();
  $(".delete-dialog").hide();
  $(".purchase-information").hide();
  $(".move-right").hide();
  $(".move-left").hide();
}

/**
 * Initializes the state of some elements and establishes some event handlers.
 */
$(document).ready(function() {
  // allow scrolling in the bio window. NOTE: this must occur before hiding!
  $('.scroll-pane').jScrollPane();
  // need to do this here because jscrollpane does some black magic on the
  // style of my elements
  $('.scroll-pane').css('padding-bottom', '10px');
  $('.scroll-pane').css('padding-top', '10px');

  $("#contact-info").hide();
  $("#purchase-info").hide();
  $("#bio").hide();
  $("#photos-banner").hide();
  $("#photos-container").hide();
  $("#splash-shadow").hide();
  $(".submenu").hide();
  $("#change-splash-photo").hide();

  $(".purchase").live("click", function(event) {
    event.preventDefault();
    $(this).siblings(".photo-shadow").fadeIn();
    $(this).siblings(".purchase-information").fadeIn();
  });

  $("a.close").live("click", function(event) {
    event.preventDefault();
    $(this).parent().fadeOut();
    $(this).parent().siblings(".photo-shadow").fadeOut();
  });

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
      // TODO add :visible to selectors
      $("#bio-link").removeClass("selected");
      $("#contact-link").removeClass("selected");
      $("#purchase-link").removeClass("selected");
      $(this).addClass("selected");
      $("#contact-info").fadeOut();
      $("#purchase-info").fadeOut();
      $("#splash-shadow").fadeOut();
      $("#bio").fadeOut();
      $(".submenu").show();
    }
  });

  $("#bio-link").click(function(event) {
    event.preventDefault();
    if ($(this).hasClass("selected")) {
      $(this).removeClass("selected");
      $("#splash-shadow").fadeOut();
      $("#bio").fadeOut();
    } else {
      $("#photos-link").removeClass("selected");
      $(".photo-link").removeClass("selected");
      $("#contact-link").removeClass("selected");
      $("#purchase-link").removeClass("selected");
      $(this).addClass("selected");

      $(".submenu").hide();
      $("#contact-info").fadeOut();
      $("#purchase-info").fadeOut();
      $("#splash-shadow").fadeIn();

      if ($("#photos-container").is(":visible")) {
        $("#photos-container").fadeOut(400, function() {
          $("#banner-container").animate(
            { top : 400 },
            {
              duration: 500,
              complete: function() {
                $("#bio").fadeIn();
              }
            });
        });
      } else {
        $("#bio").fadeIn();        
      }
    }
  });

  $("#contact-link").click(function(event) {
    event.preventDefault();
    if ($(this).hasClass("selected")) {
      $(this).removeClass("selected");
      $("#splash-shadow").fadeOut();
      $("#contact-info").fadeOut();
    } else {
      $("#photos-link").removeClass("selected");
      $(".photo-link").removeClass("selected");
      $("#bio-link").removeClass("selected");
      $("#purchase-link").removeClass("selected");
      $(this).addClass("selected");

      $(".submenu").hide();
      $("#bio").fadeOut();
      $("#purchase-info").fadeOut();
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

  $("#purchase-link").click(function(event) {
    event.preventDefault();
    if ($(this).hasClass("selected")) {
      $(this).removeClass("selected");
      $("#splash-shadow").fadeOut();
      $("#purchase-info").fadeOut();
    } else {
      $("#photos-link").removeClass("selected");
      $(".photo-link").removeClass("selected");
      $("#contact-link").removeClass("selected");
      $("#bio-link").removeClass("selected");
      $(this).addClass("selected");

      $(".submenu").hide();
      $("#contact-info").fadeOut();
      $("#bio").fadeOut();
      $("#splash-shadow").fadeIn();

      if ($("#photos-container").is(":visible")) {
        $("#photos-container").fadeOut(400, function() {
          $("#banner-container").animate(
            { top : 400 },
            {
              duration: 500,
              complete: function() {
                $("#purchase-info").fadeIn();
              }
            });
        });
      } else {
        $("#purchase-info").fadeIn();
      }
    }
  });

  $(".photo-link").click(function(event) {
    event.preventDefault();
    if (!$(this).hasClass("selected")) {
      $("#contact-link").removeClass("selected");
      $("#purchase-link").removeClass("selected");
      $(".photo-link").removeClass("selected");
      $(this).addClass("selected");

      $("#contact-info").fadeOut();
      $("#purchase-info").fadeOut();
      $("#bio").fadeOut();
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
      var categoryid = $(this).attr("id");
      $.getJSON(SCRIPT_ROOT + '/_get_photos', {categoryid : categoryid},
                displayPhotos);
    }
  });
});
