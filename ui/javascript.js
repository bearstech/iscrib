function input_enabled(name) {
    $("input[name=" + name + "]")
        .attr("disabled", false)
        .removeClass('disabled');
    $("#field_" + name)
        .attr("disabled", false)
        .removeClass('disabled');
}

function input_disabled(name) {
    $("input[name=" + name + "]")
        .attr("disabled", true)
        .addClass('disabled');
    $("#field_" + name)
        .attr("disabled", true)
        .addClass('disabled');
}


/*
 * Tooltip script
 * powered by jQuery (http://www.jquery.com)
 *
 * written by Alen Grakalic (http://cssglobe.com)
 *
 * for more info visit http://cssglobe.com/post/1695/easiest-tooltip-and-image-preview-using-jquery
 *
 */

this.tooltip = function(){
    /* CONFIG */
    // these 2 variable determine popup's distance from the cursor
    // you might want to adjust to get the right result
    xOffset = 10;
    yOffset = 20;
    /* END CONFIG */
    $("*[rel=tooltip]").hover(function(e) {
        this.t = this.title;
        this.title = "";
        $("body").append("<p id='tooltip'>"+ this.t +"</p>");
        $("#tooltip")
            .css("top",(e.pageY - xOffset) + "px")
            .css("left",(e.pageX + yOffset) + "px")
            .fadeIn("fast");
    },
    function() {
        this.title = this.t;
        $("#tooltip").remove();
    });
    $("*[rel=tooltip]").mousemove(function(e){
        $("#tooltip")
            .css("top",(e.pageY - xOffset) + "px")
            .css("left",(e.pageX + yOffset) + "px");
    });
};


$(document).ready(function(){
    tooltip();
});
