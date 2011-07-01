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
(function() {
  "use strict";

  function movedRight(data, textStatus, xhr) {
    var img, cell, next, parentRow;
    //if (data.moved) {
    img = $('img[id~="' + data.id + '"]');
    cell = img.parents(".photo-cell");
    // TODO here we are assuming that cell.next() == data["photoid2"]
    next = cell.next();
    parentRow = cell.parent();

    // show the left arrow if this was the first photo
    if (cell.is(":first-child")) {
      img.siblings(".move-left").show();
    }
      
    // detach the cell and reinsert it after the one on its right
    cell.detach();
    next.after(cell);

    // hide the right arrow if this is the last photo
    if (cell.is(":last-child")) {
      img.siblings(".move-right").hide();
    }
    //} else {
    // TODO do something
    //  alert("could not move right");
    //}
  }

  function movedLeft(data, textStatus, xhr) {
    var img, cell, prev, parentRow;
    //if (data.moved) {
    img = $('img[id~="' + data.id + '"]');
    cell = img.parents(".photo-cell");
    // TODO here we are assuming that cell.prev() == data["photoid2"]
    prev = cell.prev();
    parentRow = cell.parent();

    // show the right arrow if this was the last photo
    if (cell.is(":last-child")) {
      img.siblings(".move-right").show();
    }
      
    // detach the cell and reinsert it before the one on its left
    cell.detach();
    prev.before(cell);

    // hide the left arrow if this is the first photo
    if (cell.is(":first-child")) {
      img.siblings(".move-left").hide();
    }
    //} else {
    // TODO do something
    //  alert("could not move left");
    //}
  }

  $(document).ready(function() {
    $(".photo-cell").live("hover", function() {
      $(this).children(".edit-menu").toggle();
      // don't show the left arrow on the first photo and the right arrow on
      // the last photo
      var toToggle = $(this).children(".move-right, .move-left")
        .not("td.photo-cell:first-child div.move-left")
        .not("td.photo-cell:last-child div.move-right");

      toToggle.toggle();
    });

    $("#splash").hover(function() {
      $(this).children("#change-splash-photo").toggle();
    });

    // this event is similar to the hover action for the purchase link
    // specified in the CSS, but we put it in here since we need to change a
    // property on a different element
    $(".change-cat,.delete").live("mouseenter", function() {
      $(this).parents(".edit-menu").animate({opacity: 1}, 100);
    });
    $(".change-cat,.delete").live("mouseleave", function() {
      $(this).parents(".edit-menu").animate({opacity: 0.4}, 100);
    });

    $(".delete").live("click", function(event) {
      event.preventDefault();
      $(this).parents(".photo-cell")
        .children(".photo-shadow, .delete-dialog").fadeIn();
    });

    $(".cancel").live("click", function(event) {
      event.preventDefault();
      $(this).parents(".photo-cell")
        .children(".photo-shadow, .delete-dialog, .cat-chooser").fadeOut();
    });

    $(".confirm-delete").live("click", function(event) {
      var img, id;
      event.preventDefault();
      img = $(this).parents(".delete-dialog").siblings("img");
      id = img.attr("id");
      $.ajax({
        type: 'DELETE',
        url: SCRIPT_ROOT + '/photos/' + id,
        success: function(data, textStatus, xhr) {
          var cell = img.parents(".photo-cell");
          cell.fadeOut(400, function() {
            $(this).remove();
          });
        },
        dataType: "json"
      });
    });

    $(".category-option").live("click", function(event) {
      event.preventDefault();

      $(this).parent().siblings().children("a.selected-cat")
        .removeClass("selected-cat");
      $(this).addClass("selected-cat");
    });

    $(".change-cat").live("click", function(event) {
      var list, photoCell;
      event.preventDefault();
      
      photoCell = $(this).parents(".photo-cell");
      photoCell.children(".photo-shadow, .cat-chooser").fadeIn();
      list = photoCell.find(".category-list");
      list.empty();

      $.getJSON(
        SCRIPT_ROOT + "/categories",
        function(data, textStatus, xhr) {
          var currentCategory, i, selectedPhotoLink, categories;
          // TODO move these two lines outside of this callback function
          selectedPhotoLink = 'a[class~="photo-link"][class~="selected"]';
          currentCategory = parseInt($(selectedPhotoLink).attr("id"), 10);
          categories = data['items'];
          for (i = 0; i < categories.length; i += 1) {
            list.append("<li><a href=\"#\" id=\"" + categories[i].id
                        + "\" class=\"category-option\">" + categories[i].name
                        + "</a></li>");
            if (categories[i].id === currentCategory) {
              list.children().last().children("a").addClass("selected-cat");
            }
          }
          list.append("<li><a href=\"#\" id=\"new\" class=\"category-option\">"
                      + "new&nbsp;category&hellip;</a></li>");
        });
    });

    $("a#new").live("click", function(event) {
      event.preventDefault();
      $(this).parent().replaceWith("<input type=\"text\""
                                   + "name=\"new-category-name\""
                                   + "id=\"new-category-name\""
                                   + "maxlength=\"20\""
                                   + "placeholder=\"new category\" />");
      $("input#new-category-name").focus();
    });

    $("input#new-category-name").live("keyup", function(event) {
      // thirteen is the keycode for the enter key
      if (event.keyCode === 13) {
        var word = $(this).val();
        // turn this input box into the word
        $(this).replaceWith("<li><a href=\"#\" class=\"category-option\""
                            + "id=\"-1\">" + word + "</a></li>");
        $("a#-1").addClass("selected-cat");
      }
    });

    $(".confirm-cat-change").live("click", function(event) {
      var selectedCat, categoryid, photoContainer, name, photoid, img;
      event.preventDefault();

      selectedCat = 'a[class~="category-option"][class~="selected-cat"]';
      categoryid = parseInt($(this).parents(".cat-chooser").find(selectedCat)
                            .attr("id"), 10);
      photoContainer = $(this).parents(".photo-cell");

      // Note: this jquery selector
      //  $('a[class~="photo-link"][class~="selected"]')
      // selects a elements having class both "photo-link" and "selected"
      if (categoryid
          === parseInt($('a[class~="photo-link"][class~="selected"]')
                       .attr("id"), 10)) {
        // confirmed category to save is the same as the current category, so
        // we just leave it where it is and fade out the dialog
        photoContainer.children(".photo-shadow, .cat-chooser").fadeOut();
      } else {
        img = photoContainer.children("img");
        photoid = img.attr("id");

        // TODO check if input text box still exists. if it does, get that as
        // the name, check that it is non-empty, and set -1 as the category ID
        name = null;
        if (categoryid === -1) {
          name = $("a#-1").html();
        }

        $.post(SCRIPT_ROOT + "/photos/" + photoid,
               { categoryid: categoryid },
               function(data, textStatus, xhr) {
                 photoContainer.fadeOut(400, function() {
                   $(this).remove();
                 });
               },
               "json");
      }
    });

    $(".move-right").live("click", function(event) {
      var cell, photoid, nextid, nextDisplayPosition;
      event.preventDefault();
      cell = $(this).parents(".photo-cell");
      if (!(cell.is(":last-child"))) {
        photoid = $(this).siblings("img").attr("id");
        nextid = cell.next().find("img").attr("id");
        // get the display position of the photo on its right
        $.getJSON(SCRIPT_ROOT + "/photos/" + nextid,
                  function(data) {
                    var nextDisplayPosition = data.displayposition;
                    // update the display position of this photo to be that
                    // display position (the server swaps their positions for
                    // us)
                    $.post(SCRIPT_ROOT + '/photos/' + photoid,
                           { displayposition: nextDisplayPosition },
                           movedRight,
                           "json");
                  });
      }
    });

    $(".move-left").live("click", function(event) {
      var cell, photoid, previousid, prevDisplayPosition;
      event.preventDefault();
      cell = $(this).parents(".photo-cell");
      if (!(cell.is(":first-child"))) {
        photoid = $(this).siblings("img").attr("id");
        previousid = cell.prev().find("img").attr("id");
        // get the display position of the photo on its left
        $.getJSON(SCRIPT_ROOT + "/photos/" + previousid,
                  function(data) {
                    prevDisplayPosition = data["displayposition"];
                  });
        // update the display position of this photo to be that display
        // position (the server swaps their positions for us)
        $.post(SCRIPT_ROOT + '/photos/' + photoid,
               { displayposition: prevDisplayPosition },
               movedLeft,
               "json");
      }
    });
  });
}());
