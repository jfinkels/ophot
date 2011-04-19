function deleteCategory(data, textStatus, xhr) {
  if (data["deleted"]) {
    var row = $("a.delete-cat#" + data["categoryid"]).parents("tr");
    row.fadeOut(400, function() {
      $(this).remove();
    });
  } else {
    // TODO do something
    alert("could not delete category with id " + data["categoryid"]);
  }
}

function renamedCategory(data, textStatus, xhr) {
  // intentionally unimplemented
}

function spacingChanged(data, textStatus, xhr) {
  // intentionally unimplemented
}

function updatedPersonalInfo(data, textStatus, xhr) {
  // intentionally unimplemented
}

$(document).ready(function() {
  $(".delete-dialog").hide();
  $("#settings-shadow").hide();

  $("#spacing").change(function() {
    var spacing = $(this).val();
    $.getJSON(SCRIPT_ROOT + '/_change_spacing', {spacing: spacing},
              spacingChanged);
  });

  $(".rename-cat").live("click", function(event) {
    event.preventDefault();
    var nameCell = $(this).parent().siblings(".cat-name");
    var name = nameCell.html();
    var categoryId = nameCell.attr('id');
    nameCell.html('<input type="text" value="' + name + '"/>');
    nameCell.children("input").focus();
    //var deleteLink = $(this).parent().siblings(".delete-cat");
    //deleteLink.replaceWith('<a href="#" id="cancel">cancel</a>');
    $(this).replaceWith('<a href="#" id="' + categoryId
                        + '" class="confirm-name-change">save</a>');
  });

  $(".confirm-name-change").live("click", function(event) {
    event.preventDefault();
    var nameCell = $(this).parent().siblings(".cat-name");
    var categoryId = nameCell.attr('id');
    var input = nameCell.children("input");
    var categoryName = input.val();
    nameCell.html(categoryName);
    $(this).replaceWith('<a href="#" class="rename-cat" id="'
                        + categoryId + '">rename</a>');
    $.getJSON(SCRIPT_ROOT + '/_change_category_name',
              {categoryid: categoryId, categoryname: categoryName},
              renamedCategory);
  });

  $(".delete-cat").live("click", function(event) {
    event.preventDefault();
    $(this).addClass("selected");
    $(".delete-dialog").fadeIn();
    var newHeight = $("#settings-container").height();
    $("#settings-shadow").height(newHeight);
    $("#settings-shadow").fadeIn();
  });

  $(".cancel").click(function(event) {
    event.preventDefault();
    $(".delete-dialog").fadeOut();
    $("#settings-shadow").fadeOut();
    $(".delete-cat.selected").removeClass("selected");
  });

  $(".confirm-delete").click(function(event) {
    event.preventDefault();
    $(".delete-dialog").fadeOut();
    $("#settings-shadow").fadeOut();
    var id = $(".delete-cat.selected").attr("id");
    $(".selected").removeClass("selected");
    $.ajax({
      type: 'DELETE',
      url: SCRIPT_ROOT + '/delete_category/' + id,
      success: deleteCategory
    });
  });

  $("textarea#contact").keypress(function() {
    $(this).siblings("input.save").removeAttr("disabled");
    $(this).siblings("input.save").val("save");
  });

  $("textarea#bio").keypress(function() {
    $(this).siblings("input.save").removeAttr("disabled");
    $(this).siblings("input.save").val("save");
  });

  $('input.save[disabled!="disabled"]').click(function() {
    $(this).val("saved");
    $(this).attr("disabled", "disabled");
    var name = $(this).siblings("textarea").attr("id");
    var value = $(this).siblings("textarea").val();
    $.getJSON(SCRIPT_ROOT + '/_update_personal',
              {name: name, value: value},
              updatedPersonalInfo);
  })
});
