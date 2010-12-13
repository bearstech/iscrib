function input_enabled(name) {
    $("input[name=" + name + "]").attr("disabled", false).removeClass('disabled');
    $("#field_" + name).attr("disabled", false).removeClass('disabled');
}

function input_disabled(name) {
    $("input[name=" + name + "]").attr("disabled", true).addClass('disabled');
    $("#field_" + name).attr("disabled", true).addClass('disabled');
}
