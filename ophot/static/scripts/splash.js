/**
 * Copyright 2011 Jeffrey Finkelstein
 *
 * This file is part of Ophot.
 *
 * Ophot is free software: you can redistribute it and/or modify
 * it under the terms of the GNU Affero General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * Ophot is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU Affero General Public License for more details.
 *
 * You should have received a copy of the GNU Affero General Public License
 * along with Ophot.  If not, see <http://www.gnu.org/licenses/>.
 */
(function () {
  "use strict";
  var prevScrollLeft, MAX_POSITION;
  MAX_POSITION = 600;

 /**
  * Creates the table cell for each photo requested by the displayPhotos()
  * function. The unique ID of the photo is *photoid*, which is filled into the
  * "id" attribute of the <img> element, and the path to the file containing
  * the photo is specified in *filename*. *categories* is an array containing
  * the names of the categories to which a photo can be assigned.
  */
  function createPhotoCellString(photoid, filename) {
    return "<td class=\"photo-cell\">\n"
    /*
      + "    <div class=\"photo-shadow absolute-position\"></div>\n"
      + "    <a class=\"purchase black-background\" href=\"#\">purchase</a>\n"
      + "    <div class=\"purchase-information\">\n"
      + "      <a class=\"close\">X</a>\n"
      + "      <p>\n"
      + "        For pricing or to order prints email\n"
      + "        " + PURCHASE_EMAIL + "\n"
      + "      </p>\n"
      + "    </div>\n"
    */
      + EDIT_ELEMENTS
      + "    <img src=" + filename + " id=\"" + photoid + "\"/>\n"
      + "</td>\n";
  }

 /**
  * Fades out each of the jQuery objects specified by the given array of jQuery
  * selectors.
  */
  function _fadeOutMany(selectors) {
    var i;
    for (i = 0; i < selectors.length; i += 1) {
      $(selectors[i]).fadeOut();
    }
  }

 /**
  * Hides the jQuery objects specified by the given array of jQuery selectors.
  */
  function _hideMany(selectors) {
    var i;
    for (i = 0; i < selectors.length; i += 1) {
      $(selectors[i]).hide();
    }
  }

 /**
  * Removed the class *clazz* from each of the jQuery objects selected by the
  * elements of the specified array of jQuery selectors.
  */
  function _removeClassFromMany(selectors, clazz) {
    var i;
    for (i = 0; i < selectors.length; i += 1) {
      $(selectors[i]).removeClass(clazz);
    }
  }

 /**
  * Callback which adds new cells to the <tr> element with id "the-row", each
  * containing the filename specified in data. The data object contains a map
  * from the unique ID of the photo to display to the path to that photo.
  */
  function displayPhotos(data/*, textStatus, xhr*/) {
    var photos, i, photoid, filename, photoCellString;
    photos = data.values;

    // assume the data is in the format described in the documentation for the
    // _get_photos route
    for (i = 0; i < photos.length; i += 1) {
      photoid = photos[i].photoid;
      filename = photos[i].filename;
      photoCellString = createPhotoCellString(photoid, filename);
      $("#the-row").append(photoCellString);
    }

    // hide these things as soon as they are created
    _hideMany([".edit-menu", ".cat-chooser", ".purchase", ".photo-shadow",
               ".delete-dialog", ".purchase-information", ".move-right",
               ".move-left"]);
  }

 /**
  * Fades out the photos container, slides the banner container up, and fades
  * in the object specified by *inSelector*.
  */
  function fadeOutFadeIn(inSelector) {
    $("#photos-container").fadeOut(400, function() {
      $("#banner").animate(
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
  * of the window, and sets up the listener for the window resize event to
  * reset the width of the photos-container.
  */
  function _photosContainerWidth() {
    var container, paddingLeft, paddingRight, newWidth;
    container = $("#photos-container");
    container.css("min-width", $(window).width());
    $(window).resize($.debounce(250, function() {
      paddingLeft = parseInt(container.css("padding-left"), 10);
      paddingRight = parseInt(container.css("padding-right"), 10);
      newWidth = $(window).width() - (paddingLeft + paddingRight);
      container.animate({"min-width": newWidth});
    }));
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
    $(".photo-cell").live("hover", function() {
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
            $("#banner").animate({ top : 400 }, 500);
          });
        });
      } else {
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
  * Toggles the link and displays the information div specified by
  * *linkSelector* and *infoSelector*, respectively, and deselects the links
  * and hides the information divs specified by the *otherLinkSelectors* array
  * and *otherInfoSelectors* array, respectively.
  */
  function _basicInfoClick(linkSelector, infoSelector, otherLinkSelectors,
                           otherInfoSelectors) {
    $(linkSelector).click(function(event) {
      var remove;
      event.preventDefault();
      if ($(this).hasClass("selected")) {
        $(this).removeClass("selected");
        _fadeOutMany(["#splash-shadow", infoSelector]);
      } else {
        remove = otherLinkSelectors.concat(["#photos-link", ".photo-link"]);
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
        _removeClassFromMany(["#contact-link", "#purchase-link",
                              ".photo-link"], "selected");
        $(this).addClass("selected");

        _fadeOutMany(["#contact-info", "#purchase-info", "#bio"]);
        if ($("#photos-container").is(":hidden")) {
          $("#banner").animate(
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
   * Returns the opacity value for the container shadow over the main splash
   * photo when the window is scrolled to *position*.
   *
   * The returned opacity scales linearly down on the domain [0, MAX_POSITION]
   * taking values in the range [0, 1]. For example, at position 0 the opacity
   * is 1, at position MAX_POSITION the opacity is 0, and at position
   * MAX_POSITION / 2 the opacity is 0.5.
   *
   * Pre-condition: position is an integer.
   */
  function _positionToOpacity(position) {
    if (position <= 0) {
      return 1;
    } else if (position >= MAX_POSITION) {
      return 0;
    }

    return 1 - (position / MAX_POSITION);
  }

  /**
   * When the window is scrolled to the right or left, set the opacity of the
   * shadow over the main splash photo so that it fades out when scrolling
   * away, and fades back in when scrolling back to it.
   */
  function _setupScrollShadow() {
    $(window).scroll(function(event) {
      var currScrollLeft, newOpacity;
      currScrollLeft = $(this).scrollLeft();
      if (currScrollLeft !== prevScrollLeft) {
        newOpacity = _positionToOpacity(currScrollLeft);
        $(".container").css({ opacity: newOpacity });
      }
      prevScrollLeft = currScrollLeft;
    });
  }

 /**
  * Initializes the state of some elements and establishes some event handlers.
  */
  $(document).ready(function() {
    // add the scroll pane to the biographical information element
    // NOTE: this MUST occur BEFORE hiding elements
    $('.scroll-pane').jScrollPane();

    // hide the elements which need to be hidden initially
    _hideMany(["#contact-info", "#purchase-info", "#bio", "#photos-banner",
               "#photos-container", "#splash-shadow", ".submenu",
               "#change-splash-photo"]);

    // set the minimum width of the photos container to be the width of the
    // window, and reset the minimum width after resize
    _photosContainerWidth();

    // add a progressive shadow for scrolling away from the main content
    _setupScrollShadow();

    // handle a click on the purchase info link
    // TODO wait until cart works before deploying this
    //_purchaseClick();

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
}());
