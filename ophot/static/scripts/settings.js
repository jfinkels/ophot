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
    if (data.added) {
      name = data.categoryname;
      id = data.categoryid;

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
    } else {
      // TODO do something
      alert("could not add category with name " + data.categoryname);
    }
  }

  function deleteCategory(data, textStatus, xhr) {
    var id, row;
    if (data.deleted) {
      id = data.categoryid;
      row = $("a.delete-cat[id=" + id + "]").parents("tr.category-row");
      row.fadeOut(400, function() {
        $(this).remove();
      });
    } else {
      // TODO do something
      alert("could not delete category with id " + data.categoryid);
    }
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
        $.getJSON(SCRIPT_ROOT + '/_add_category', {categoryname: categoryName},
                  addedCategory);
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
      var id;
      event.preventDefault();
      $(".delete-dialog").fadeOut();
      $("#settings-shadow").fadeOut();
      id = $(".delete-cat.selected").attr("id");
      $(".selected").removeClass("selected");
      $.ajax({
        type: 'DELETE',
        url: SCRIPT_ROOT + '/delete_category/' + id,
        success: deleteCategory
      });
    });

    $("#spacing").change($.debounce(500, function() {
      $.getJSON(SCRIPT_ROOT + '/_change_spacing', {spacing: $(this).val()},
                spacingChanged);
    }));

    textareaSelectors = 'textarea[name~="bio"], textarea[name~="contact"]';
    $(textareaSelectors).keypress($.debounce(500, function() {
      $.getJSON(SCRIPT_ROOT + '/_update_personal',
                {name: $(this).attr("name"), value: $(this).val()},
                updatedPersonalInfo);
    }));

    $(textareaSelectors).bind('paste', function() {
      $(this).keypress();
    });
  });
}());

