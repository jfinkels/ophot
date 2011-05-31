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
  var cats = globalVariables.categories;
  for (var i = 0; i < photos.length; ++i) {
    var photoid = photos[i].photoid;
    var filename = photos[i].filename;
    var photoCellString = createPhotoCellString(photoid, filename, cats);
    $("#the-row").append(photoCellString);
  }

  // hide these things as soon as they are created
  _hideMany([".edit-menu", ".cat-chooser", ".purchase", ".photo-shadow",
             ".delete-dialog", ".purchase-information", ".move-right",
             ".move-left"]);
}

/**
 * Fades out the photos container, slides the banner container up, and fades in
 * the object specified by *inSelector*.
 */
function fadeOutFadeIn(inSelector) {
  $("#photos-container").fadeOut(400, function() {
    $("#banner-container").animate(
      { top : 400 },
      {
        duration: 500,
        complete: function() {
          $(inSelector).fadeIn();
        }
      });
  });
}

/**
 * Sets the minimum width of the photos-container div to be the current width
 * of the window, and sets up the listener for the window resize event to reset
 * the width of the photos-container.
 */
function _photosContainerWidth() {
  var container = $("#photos-container");
  container.css("min-width", $(window).width());
  $(window).resize($.debounce(250, function() {
    var paddingLeft = parseInt(container.css("padding-left"));
    var paddingRight = parseInt(container.css("padding-right"));
    var newWidth = $(window).width() - (paddingLeft + paddingRight);
    container.animate({"min-width": newWidth});
  }));
}

/**
 * Hides the jQuery objects specified by the given array of jQuery selectors.
 */
function _hideMany(selectors) {
  for (var i = 0; i < selectors.length; ++i) {
    $(selectors[i]).hide();
  }
}

/**
 * Sets up the purchase link on each photo to listen for clicks and show the
 * purchase information.
 */
function _purchaseClick() {
  $(".purchase").live("click", function(event) {
    event.preventDefault();
    $(this).siblings(".photo-shadow").fadeIn();
    $(this).siblings(".purchase-information").fadeIn();
  });
}

/**
 * Sets up the close link (the X in the upper right corner of a div) to listen
 * for clicks and close its parent container.
 */
function _closeClick() {
  $("a.close").live("click", function(event) {
    event.preventDefault();
    $(this).parent().fadeOut();
    $(this).parent().siblings(".photo-shadow").fadeOut();
  });
}

/**
 * Sets up each photo to listen for the hover event and toggle the purchase
 * information link.
 */
function _photoHover() {
  $(".photo-container").live("hover", function() {
    $(this).children(".purchase").toggle();
  });
}

/**
 * Sets up the photos link in the banner to listen for click events and show
 * the list of category links.
 */
function _photosClick() {
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
      _removeClassFromMany(["#bio-link", "#contact-link", "#purchase-link"],
                           "selected");
      $(this).addClass("selected");
      _fadeOutMany(["#contact-info", "#purchase-info", "#splash-shadow",
                    "#bio"]);
      $(".submenu").show();
    }
  });
}

/**
 * Fades out each of the jQuery objects specified by the given array of jQuery
 * selectors.
 */
function _fadeOutMany(selectors) {
  for (var i = 0; i < selectors.length; ++i) {
    $(selectors[i]).fadeOut();
  }
}

/**
 * Removed the class *clazz* from each of the jQuery objects selected by the
 * elements of the specified array of jQuery selectors.
 */
function _removeClassFromMany(selectors, clazz) {
  for (var i = 0; i < selectors.length; ++i) {
    $(selectors[i]).removeClass(clazz);
  }
}

/**
 * Toggles the link and displays the information div specified by
 * *linkSelector* and *infoSelector*, respectively, and deselects the links and
 * hides the information divs specified by the *otherLinkSelectors* array and
 * *otherInfoSelectors* array, respectively.
 */
function _basicInfoClick(linkSelector, infoSelector, otherLinkSelectors,
                         otherInfoSelectors) {
  $(linkSelector).click(function(event) {
    event.preventDefault();
    if ($(this).hasClass("selected")) {
      $(this).removeClass("selected");
      _fadeOutMany(["#splash-shadow", infoSelector]);
    } else {
      var remove = otherLinkSelectors.concat(["#photos-link", ".photo-link"]);
      _removeClassFromMany(remove, "selected");
      $(this).addClass("selected");

      $(".submenu").hide();
      _fadeOutMany(otherInfoSelectors);
      $("#splash-shadow").fadeIn();

      // fade out the photos-container and fade in the contact info
      fadeOutFadeIn(infoSelector);
    }
  });
}

/**
 * Sets up a photo category link to listen for clicks and show the photos for
 * the category clicked.
 */
function _photoLinkClick() {
  $(".photo-link").click(function(event) {
    event.preventDefault();
    if (!$(this).hasClass("selected")) {
      _removeClassFromMany(["#contact-link", "#purchase-link", ".photo-link"],
                           "selected");
      $(this).addClass("selected");

      _fadeOutMany(["#contact-info", "#purchase-info", "#bio"]);
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
}

/**
 * Adds jScrollPane functionality to any element of class "scroll-pane".
 *
 * This requires the jScrollPane jQuery plugin.
 */
function _addScrollPane() {
  // allow scrolling in the bio window. NOTE: this must occur before hiding!
  $('.scroll-pane').jScrollPane();
  // need to do this here because jscrollpane does some black magic on the
  // style of my elements
  $('.scroll-pane').css('padding-bottom', '10px');
  $('.scroll-pane').css('padding-top', '10px');
}

/**
 * Initializes the state of some elements and establishes some event handlers.
 */
$(document).ready(function() {
  // add the scroll pane to the biographical information element
  _addScrollPane();

  // hide the elements which need to be hidden initially
  _hideMany(["#contact-info", "#purchase-info", "#bio", "#photos-banner",
             "#photos-container", "#splash-shadow", ".submenu",
             "#change-splash-photo"]);

  // set the minimum width of the photos container to be the width of the
  // window, and reset the minimum width after resize
  _photosContainerWidth();

  // handle a click on the purchase info link
  _purchaseClick();

  // handle a click on the close link (the X in the top right corner)
  _closeClick();

  // handle a hover over a photo
  _photoHover();

  // handle a click on the photos link and on a link to specific category
  _photosClick();
  _photoLinkClick();

  // handle a click on the bio, contact, and purchase links
  _basicInfoClick("#bio-link", "#bio",
                  ["#contact-link", "#purchase-link"],
                  ["#contact-info", "#purchase-info"]);
  _basicInfoClick("#contact-link", "#contact-info",
                  ["#bio-link", "#purchase-link"],
                  ["#bio", "#purchase-info"]);
  _basicInfoClick("#purchase-link", "#purchase-info",
                  ["#bio-link", "#contact-link"],
                  ["#bio", "#contact-info"]);
});
