function disableField(element) {
  element.value = "";
  element.disable = true;
  element.style.background = "#eee";
}

function updateSearchField(value) {
  search_field = document.getElementById("search_name")
  if (value == "BDP") {
    disableField(search_field);
  }
  else {
    search_field.disable = null;
    search_field.style.background = null;
  }
}

function switch_off(field_id_list) {
    for(i=0; i < field_id_list.length; i++) {
        field_id = field_id_list[i];
        field_id = 'display_' + field_id;
        field = document.getElementById(field_id);
        field.style.visibility = 'hidden';
    }
}


function switch_on(field_id_list) {
    for(i=0; i<field_id_list.length; i++) {
        field_id = field_id_list[i];
        field_id = 'display_' + field_id;
        field = document.getElementById(field_id);
        field.style.visibility = 'visible';
   }
}

