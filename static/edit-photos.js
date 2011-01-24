function deletePhoto(data, textStatus, xhr) {
  if (data["deleted"]) {
    var cell = $("img#" + data["photo_id"]).parents(".photo-cell");
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
    $(this).children(".delete").toggle();
  });

  $(".delete").live("click", function(event) {
    event.preventDefault();
    
    $(this).siblings(".photo-shadow").fadeIn();
    $(this).siblings(".confirm-delete").fadeIn();
  });

  $(".cancel").live("click", function(event) {
    event.preventDefault();
    $(".photo-shadow").fadeOut();
    $(".confirm-delete").fadeOut();
  });

  $(".confirm").live("click", function(event) {
    event.preventDefault();
    var id = $(this).parents(".confirm-delete").siblings("img").attr("id");
    $.ajax({
      type: 'DELETE',
      url: SCRIPT_ROOT + '/delete/' + id,
      success: deletePhoto
    });
  });
});
