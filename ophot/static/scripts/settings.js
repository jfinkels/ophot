function generateCategoryRow(name, id) {
  return '<tr class="category-row">\n'
    + '<td class="cat-name" id="' + id + '">' + name + '</td>\n'
    + '<td class="cat-options">\n'
    + '<a href="#" class="rename-cat" id="' + id + '">rename</a>\n'
    + '<a href="#" class="delete-cat" id="' + id + '">delete</a>\n'
    + '</td>\n'
    + '</tr>\n';
}

function addedCategory(data, textStatus, xhr) {
  if (data["added"]) {
    var name = data["categoryname"];
    var id = data["categoryid"];

    // replace the text input box with the "new category..." link again
    $("input#new-cat").replaceWith('<a href="#" id="new-cat">new category&hellip;</a>');

    // iterate over each category in order to place it in alphabetical order
    // TODO alphabetical list insert code could be used from
    // http://stackoverflow.com/questions/2886739/using-jquery-to-dynamically-insert-into-list-alphabetically
    // TODO this currently doesn't work if there are no rows
    $("tr.category-row").last().after(generateCategoryRow(name, id));
  } else {
    // TODO do something
    alert("could not add category with name " + data["categoryname"]);
  }
}

function deleteCategory(data, textStatus, xhr) {
  if (data["deleted"]) {
    var id = data["categoryid"];
    var row = $("a.delete-cat[id=" + id + "]").parents("tr.category-row");
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

  $("a#new-cat").click(function(event) {
    event.preventDefault();
    $(this).replaceWith('<input type="text" id="new-cat" '
                        + 'placeholder="new category&hellip;">');
  });

  $("input#new-cat").live("keyup", function(event) {
    // 13 is the keycode for the enter key
    if (event.keyCode == 13 && $(this).val() != "") {
      var categoryName = $(this).val();
      $.getJSON(SCRIPT_ROOT + '/_add_category', {categoryname: categoryName},
                addedCategory);
    }
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
