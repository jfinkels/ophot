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
