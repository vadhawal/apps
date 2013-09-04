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

var comment_on_object_handler = function(event){
        var form = $(this);
        $.ajax({
            type: form.attr('method'),
            url: form.attr('action'),
            data: form.serialize(),
            success: function (data) {
                var subcomments_element = form.parents('.subcomments_container').find(".subcomments");
                form.trigger('reset');
                subcomments_element.append(data.html);
                subcomments_element.find('.upvote').off("click").on("click", voting_handlers);
                subcomments_element.find('.downvote').off("click").on("click", voting_handlers);
                subcomments_element.find('.clearvote').off("click").on("click", voting_handlers);
                subcomments_element.find('.pScore').off("click").on("click", display_popup_handler);
                subcomments_element.find('.broadcasters').off("click").on("click", display_popup_handler);
            },
            error: function(data) {
                console.log(data);
            }
        });

    event.stopPropagation();
    event.preventDefault();
    return false;
};

var install_comment_on_object_handler = function() {
    $('.comment_on_object').off('submit').on('submit', comment_on_object_handler);
};


