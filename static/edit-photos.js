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

$(document).ready(function() {
  $(".photo-container").live("hover", function() {
    $(this).children(".edit-menu").toggle();
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
      });
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
        $.getJSON(SCRIPT_ROOT + '/_change_category',
          { photoid: photoid, categoryid: categoryid },
          changeCategory
        );
    }
  });
});
