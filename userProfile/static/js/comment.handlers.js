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
	    if(login_required_handler())
        	return false;
        var $form = $(this);
        $.ajax({
            type: $form.attr('method'),
            url: $form.attr('action'),
            data: $form.serialize(),
            success: function (data) {
                var subcomments_element = $form.parents('.subcomments_container').find(".subcomments");
                $form.trigger('reset');
                subcomments_element.append(data.html);
                subcomments_element.find('.upvote').off("click").on("click", voting_handlers);
                subcomments_element.find('.downvote').off("click").on("click", voting_handlers);
                subcomments_element.find('.clearvote').off("click").on("click", voting_handlers);
                subcomments_element.find('.pScore').off("click").on("click", display_popup_handler);
                subcomments_element.find('.broadcasters').off("click").on("click", display_popup_handler);
                install_toggle_comment_handler();
                var $formParent = $form.parents(".subcomments_container");
                var $total_comments = $formParent.find('.total_comments');
                var $loaded_comments = $formParent.find('.loaded_comments');
                var total_comments = parseInt($total_comments.text());
                var loaded_comments = parseInt($loaded_comments.text());
                total_comments = total_comments + 1;
                loaded_comments = loaded_comments + 1;
                $total_comments.text(total_comments);
                $loaded_comments.text(loaded_comments);
                $form.find('.subcomment_text').trigger('autosize.resize');
            },
            error: function(data) {
                console.log(data);
            }
        });

    event.stopPropagation();
    event.preventDefault();
    return false;
};

var view_previous_comments_handler = function(event){
    var add_link = $(this);
    $.get(add_link.attr('href'), {}, function(data) {
        add_link.closest('.subcomments_container').find('.subcomments').prepend(data);
        var link = add_link.attr('href');
        var linksplit = link.split("/");
        var sIndex = parseInt(linksplit[linksplit.length-2]) + 5;
        linksplit[linksplit.length-2] = sIndex;
        var lIndex = parseInt(linksplit[linksplit.length-3]) + 5;
        linksplit[linksplit.length-3] = lIndex;

        link = linksplit.join('/');
        add_link.attr('href', link);
        var total_comments = parseInt(add_link.parent().find('.total_comments').text());
        var loaded_comments = parseInt(add_link.parent().find('.loaded_comments').text());
        if(loaded_comments + 5 <= total_comments) {
            add_link.parent().find('.loaded_comments').text(loaded_comments + 5);
        }
        else {
            $('.viewPreviousComments').parent().next().remove(); // remove the next HR
            $('.viewPreviousComments').parent().remove(); // remove the entire view previos comment
            //add_link.parent().find('.loaded_comments').text(total_comments);
        }
        install_voting_handlers();
        install_comment_on_object_handler();
        install_toggle_comment_handler();
    });

    event.stopPropagation();
    event.preventDefault();
    return false;
};

var comment_radio_handler = function(event){
	var $text_element = $(this).parents('.radio_module').parent().find('.subcomment_text');
	if($text_element)
		$text_element.focus();

    event.stopPropagation();
    event.preventDefault();
    return false;
};

var comment_on_object_key_handler = function(event){
	if(event.which == 13 && !event.shiftKey) {
		var $text_element = $(this);
		$text_element.blur();
		var $form = $text_element.parents('.comment_on_object');
		if($form) {
			$form.find('.subcomment_text').trigger('autosize.resize');
			$form.submit();
		}
		
		event.stopPropagation();
    	event.preventDefault();
		return false;	
	}

}

var install_comment_on_object_handler = function() {
    $('.comment_on_object').off('submit').on('submit', comment_on_object_handler);
    $('.subcomment_text').off('keyup').on('keyup', comment_on_object_key_handler);
    $('.subcomment_text').autosize({append: "\n"});
    $('.viewPreviousComments').off('click').on('click', view_previous_comments_handler);
    $('.comment_radio').off('click').on('click', comment_radio_handler);
};


