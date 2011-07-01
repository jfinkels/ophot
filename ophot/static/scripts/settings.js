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
    var name, id, categoryRow, added;
    //if (data.added) {
      name = data.name;
      id = data.id;

      // replace the text input box with the "new category..." link again
      $("input#new-cat").replaceWith(
        '<a href="#" id="new-cat">new category&hellip;</a>');

      // insert in alphabetical order code adapted from
      // http://stackoverflow.com/questions/2886739/using-jquery-to-dynamically-insert-into-list-alphabetically/2890810#2890810
      categoryRow = generateCategoryRow(name, id);
      added = false;
      $("tr.category-row").each(function() {
        if ($(this).children(".cat-name").text() > name) {
          $(this).before(categoryRow);
          added = true;
          return false;
        }
      });
      if (!added) {
        $("tr#new-cat-row").before(categoryRow);
      }
    //} else {
    // TODO do something
    //  alert("could not add category with name " + data.name);
    //}
  }

  function deleteCategory(data, textStatus, xhr) {
  }

  function renamedCategory(data, textStatus, xhr) {
    // intentionally unimplemented
  }

  function spacingChanged(data, textStatus, xhr) {
    // TODO show a little "saved" message
  }

  function updatedPersonalInfo(data, textStatus, xhr) {
    // TODO show a little "saved" message
  }

  $(document).ready(function() {
    var textareaSelectors;
    $(".delete-dialog").hide();
    $("#settings-shadow").hide();

    $("a#new-cat").live("click", function(event) {
      event.preventDefault();
      $(this).replaceWith('<input type="text" id="new-cat" '
                          + 'placeholder="new category&hellip;">');
    });

    $("input#new-cat").live("keyup", function(event) {
      // 13 is the keycode for the enter key
      if (event.keyCode === 13 && $(this).val() !== "") {
        var categoryName = $(this).val();
        $.post(SCRIPT_ROOT + '/categories',
               { name: categoryName },
               addedCategory,
               "json");
      }
    });

    $(".rename-cat").live("click", function(event) {
      var nameCell, name, categoryId;
      event.preventDefault();
      nameCell = $(this).parent().siblings(".cat-name");
      name = nameCell.html();
      categoryId = nameCell.attr('id');
      nameCell.html('<input type="text" value="' + name + '"/>');
      nameCell.children("input").focus();
      //var deleteLink = $(this).parent().siblings(".delete-cat");
      //deleteLink.replaceWith('<a href="#" id="cancel">cancel</a>');
      $(this).replaceWith('<a href="#" id="' + categoryId
                          + '" class="confirm-name-change">save</a>');
    });

    $(".confirm-name-change").live("click", function(event) {
      var nameCell, categoryId, input, categoryName;
      event.preventDefault();
      nameCell = $(this).parent().siblings(".cat-name");
      categoryId = nameCell.attr('id');
      input = nameCell.children("input");
      categoryName = input.val();
      nameCell.html(categoryName);
      $(this).replaceWith('<a href="#" class="rename-cat" id="'
                          + categoryId + '">rename</a>');
      $.post(SCRIPT_ROOT + '/categories/' + categoryId,
             { name: categoryName },
             renamedCategory,
             "json");
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
      var id;
      event.preventDefault();
      $(".delete-dialog").fadeOut();
      $("#settings-shadow").fadeOut();
      id = $(".delete-cat.selected").attr("id");
      $(".selected").removeClass("selected");
      $.ajax({
        type: 'DELETE',
        url: SCRIPT_ROOT + '/categories/' + id,
        dataType: "json",
        success: function(data, textStatus, xhr) {
          // TODO test that HTTP status is 204
          var row;
          row = $("a.delete-cat[id=" + id + "]").parents("tr.category-row");
          row.fadeOut(400, function() {
            $(this).remove();
          });
        }});
    });

    // the spacing input should save on changes
    // NOTE the change event is not triggered until focus leaves this!
    $("#spacing").change($.debounce(500, function() {
      $.post(SCRIPT_ROOT + '/user',
             { spacing: $(this).val() },
             spacingChanged,
             "json");
    }));
    
    // the bio and contact info textarea elements should save every half a
    // second on key presses
    $('textarea[name~="bio"]').keypress($.debounce(500, function() {
      $.post(SCRIPT_ROOT + '/user',
             { bio: $(this).val() },
             updatedBio,
             "json");
    }));
    $('textarea[name~="contact"]').keypress($.debounce(500, function() {
      $.post(SCRIPT_ROOT + '/user',
             { contact: $(this).val() },
             updatedContact,
             "json");
    }));

    // the 'paste' event is undocumented but may work in some browsers
    textareaSelectors = 'textarea[name~="contact"], textarea[name~="bio"]';
    $(textareaSelectors).bind('paste', function() {
      // just trigger the keypress event
      $(this).keypress();
    });
  });
}());
