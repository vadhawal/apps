var toggle_comment_handler = function(event) {

    var trunc = $(this).parent().find('.trunc-comment');
    var exp = $(this).parent().find('.exp-comment');
    var toggle_comment = $(this).parent().find('.toggle-comment');
    trunc.toggle();
    exp.toggle();
    if(toggle_comment.html() == "More...")
        toggle_comment.html("Less...");
    else
        toggle_comment.html("More...");

    event.stopPropagation();
    event.preventDefault();
    return false;
};

var install_toggle_comment_handler = function() {
    $('.toggle-comment').off('click').on('click', toggle_comment_handler);
}

