function deletePhoto(data, textStatus, xhr) {
  if (data["deleted"]) {
    var cell = $("img#" + data["photoid"]).parents(".photo-cell");
    cell.fadeOut(400, function() {
      $(this).remove();
    });
  } else {
    // TODO do something
    alert("could not delete");
  }
}

function changeCategory(data, textStatus, xhr) {
  if (data["changed"]) {
    var cell = $('img[id~="' + data["photoid"] + '"]').parents(".photo-cell");
    cell.fadeOut(400, function() {
      $(this).remove();
    });
  } else {
    // TODO do something
    alert("could not delete");
  }
}

function movedRight(data, textStatus, xhr) {
  if (data["moved"]) {
    var img = $('img[id~="' + data["photoid1"] + '"]');
    var cell = img.parents(".photo-cell");
    // TODO here we are assuming that cell.next() == data["photoid2"]
    var next = cell.next();
    var parentRow = cell.parent();

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
  } else {
    // TODO do something
    alert("could not move right");
  }
}

function movedLeft(data, textStatus, xhr) {
  if (data["moved"]) {
    var img = $('img[id~="' + data["photoid1"] + '"]');
    var cell = img.parents(".photo-cell");
    // TODO here we are assuming that cell.prev() == data["photoid2"]
    var prev = cell.prev();
    var parentRow = cell.parent();

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
  } else {
    // TODO do something
    alert("could not move left");
  }
}

$(document).ready(function() {
  $(".photo-container").live("hover", function() {
    $(this).children(".edit-menu").toggle();
    // don't show the left arrow on the first photo and the right arrow on the
    // last photo
    var toToggle = $(this).children(".move-right, .move-left")
      .not("td.photo-cell:first-child div.move-left")
      .not("td.photo-cell:last-child div.move-right");

    toToggle.toggle();
    // HACK should use .toggle() here, but it causes a problem with the
    // left-most and right-most photo, which should hide its left and right
    // arrow, respectively when moving into that position
    // if (toToggle.is(":visible")) {
    //   toToggle.hide();
    // } else {
    //   toToggle.show();
    // }
  });

  $("#splash").hover(function() {
    $(this).children("#change-splash-photo").toggle();
  });

  // this event is similar to the hover action for the purchase link specified
  // in the CSS, but we put it in here since we need to change a property on a
  // different element
  $(".change-cat,.delete").live("mouseenter", function() {
    $(this).parents(".edit-menu").animate({opacity: 1}, 100);
  });
  $(".change-cat,.delete").live("mouseleave", function() {
    $(this).parents(".edit-menu").animate({opacity: .4}, 100);
  });

  $(".delete").live("click", function(event) {
    event.preventDefault();
    
    $(this).parents(".photo-container").children(".photo-shadow").fadeIn();
    $(this).parents(".photo-container").children(".delete-dialog").fadeIn();
  });

  $(".cancel").live("click", function(event) {
    event.preventDefault();
    $(this).parents(".photo-container").children(".photo-shadow").fadeOut();
    $(this).parents(".photo-container").children(".delete-dialog").fadeOut();
    $(this).parents(".photo-container").children(".cat-chooser").fadeOut();
  });

  $(".confirm-delete").live("click", function(event) {
    event.preventDefault();
    var id = $(this).parents(".delete-dialog").siblings("img").attr("id");
    $.ajax({
      type: 'DELETE',
      url: SCRIPT_ROOT + '/delete/' + id,
      success: deletePhoto
    });
  });

  $(".category-option").live("click", function(event) {
    event.preventDefault();

    $(this).parent().siblings().children("a.selected-cat")
      .removeClass("selected-cat");
    $(this).addClass("selected-cat");
  });

  $(".change-cat").live("click", function(event) {
    event.preventDefault();
    
    $(this).parents(".photo-container").children(".photo-shadow").fadeIn();
    $(this).parents(".photo-container").children(".cat-chooser").fadeIn();
    var list = $(this).parents(".photo-container").find(".category-list");
    list.empty();

    $.getJSON(
      SCRIPT_ROOT + "/_get_categories",
      function(data, textStatus, xhr) {
        var currentCategory =
          parseInt($('a[class~="photo-link"][class~="selected"]').attr("id"));
        for (var i in data) {
          list.append("<li><a href=\"#\" id=\"" + i
                      + "\" class=\"category-option\">" + data[i]
                      + "</a></li>");
          if (i == currentCategory) {
            list.children().last().children("a").addClass("selected-cat");
          }
        }
        list.append("<li><a href=\"#\" id=\"new\" class=\"category-option\">"
                    + "new&nbsp;category</a></li>");
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
    if (event.keyCode == 13) {
      var word = $(this).val();
      // turn this input box into the word
      $(this).replaceWith("<li><a href=\"#\" class=\"category-option\""
                          + "id=\"-1\">" + word + "</a></li>");
      $("a#-1").addClass("selected-cat");
    }
  });

  $(".confirm-cat-change").live("click", function(event) {
    event.preventDefault();

    var categoryid =
      parseInt($(this).parents(".cat-chooser")
               .find('a[class~="category-option"][class~="selected-cat"]')
               .attr("id"));

    // Note: this jquery selector
    //  $('a[class~="photo-link"][class~="selected"]')
    // selects a elements having class both "photo-link" and "selected"
    if (categoryid
        == $('a[class~="photo-link"][class~="selected"]').attr("id")) {
      // confirmed category to save is the same as the current category, so we
      // just leave it where it is and fade out the dialog
      $(this).parents(".photo-container").children(".photo-shadow").fadeOut();
      $(this).parents(".photo-container").children(".cat-chooser").fadeOut();
    } else {
      var photoid =
        $(this).parents(".photo-container").children("img").attr("id");

      // TODO check if input text box still exists. if it does, get that as the
      // name, check that it is non-empty, and set -1 as the category ID

      var name = null;
      if (categoryid == -1) {
        name = $("a#-1").html();
      }

      $.getJSON(SCRIPT_ROOT + '/_change_category',
                { photoid: photoid,
                  categoryid: categoryid,
                  categoryname: name },
                changeCategory
               );
    }
  });

  $(".move-right").live("click", function(event) {
    event.preventDefault();
    var cell = $(this).parents(".photo-cell");
    if (!(cell.is(":last-child"))) {
      var photoid = $(this).siblings("img").attr("id");
      var nextid = cell.next().find("img").attr("id");
      $.getJSON(SCRIPT_ROOT + '/_swap_display_positions',
                { photoid1: photoid, photoid2: nextid },
                movedRight
               );
    }
  });

  $(".move-left").live("click", function(event) {
    event.preventDefault();
    var cell = $(this).parents(".photo-cell");
    if (!(cell.is(":first-child"))) {
      var photoid = $(this).siblings("img").attr("id");
      var previousid = cell.prev().find("img").attr("id");
      $.getJSON(SCRIPT_ROOT + '/_swap_display_positions',
                { photoid1: photoid, photoid2: previousid },
                movedLeft
               );
    }
  });
});
