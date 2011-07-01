function enable_disable_input(name) {
    var item = $("input[name=" + name + "]");
    if (item.attr("disabled")){
        item.removeAttr("disabled");
        item.removeClass("disabled");
    }
    else {
        item.attr("disabled", "true");
        item.addClass("disabled");
    };
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
    $("a[rel='fancybox']").click(function() {
      $.fancybox({
        'type': 'iframe',
        'transitionIn': 'elastic',
        'transitionOut': 'elastic',
        'speedIn': 600,
        'speedOut': 200,
        'width': 670,
        'height': 400,
        'overlayColor': '#729FCF',
        'overlayOpacity': 0.8,
        'href': this.href + '?view=print',
        'onCleanup': function () {
          var fancy_iframe = $("#fancybox-frame");
          var message = fancy_iframe.find("#message .info");
          this.reload_parent_window_on_close = message ? true : false;
        },
        'onClosed': function() {
          // Reload parent if changes have been done
           if (this.reload_parent_window_on_close)
               window.location.reload();
        },
      });
      return false;
    });
});
