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

var install_toggle_comment_handler = function($parent_element) {
    if($parent_element)
    {
       $parent_element.find('.toggle-comment').off('click', toggle_comment_handler).on('click', toggle_comment_handler); 
    }
    else
    {
        $('.toggle-comment').off('click', toggle_comment_handler).on('click', toggle_comment_handler);
    }
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
                install_voting_handlers(subcomments_element);
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

var edit_review_handler = function(event) {
	if(login_required_handler())
        return false;
    $("<div id='pop_up'><span class='button b-close'><span>X</span></span></div>").appendTo("body").addClass('popup');
    $('#pop_up').bPopup({
        content:'ajax',
        loadUrl:$(this).attr("href"),
        zIndex: 2,
        onClose: function(){ $('#pop_up').remove(); },
        scrollBar:'true',
    });
    event.preventDefault();
    return false;
};

var write_review_handler = function(event) {
	if(login_required_handler())
        return false;
    $("<div id='pop_up'><span class='button b-close'><span>X</span></span></div>").appendTo("body").addClass('popup');
    $('#pop_up').bPopup({
        content:'ajax',
        loadUrl:$(this).attr("href"),
        zIndex: 2,
        onClose: function(){ $('#pop_up').remove(); },
        scrollBar:'true',
        loadCallback: function(){
            $('.review_on_object').submit(review_submit_handler);
        }
    });
    event.preventDefault();
    return false;
};

var review_submit_handler = function(){
        if(login_required_handler())
            return false;
        var $form = $(this);
        $.ajax({
            type: $form.attr('method'),
            url: $form.attr('action'),
            data: $form.serialize(),
            success: function (data) {
                var ret_data = data;
                if(ret_data.success) {
                    var subcomments_element = $("#comments");
                    $form.trigger('reset');
                    subcomments_element.append(ret_data.html);
                    install_voting_handlers(subcomments_element);
                    install_toggle_comment_handler();
                    install_review_handlers(subcomments_element);
                    $form.find('.subcomment_text').trigger('autosize.resize');
                    $('#pop_up').bPopup().close();
                    $('#pop_up').remove();
                }
                else {
                    var errors = ret_data.errors;
                    $('#pop_up').find('.error').removeClass('error');
                    $.each( errors, function( key, value ) {
                        $('#pop_up').find('[name="' + key + '"]').parents('.controls').addClass('error');
                    });
                }
            },
            error: function(data) {
                console.log(data);
            }
        });
    return false;
};

var view_previous_comments_handler = function(event){
    var add_link = $(this);
    $.get(add_link.attr('href'), {}, function(data) {
        var $subcomments = add_link.closest('.subcomments_container').find('.subcomments');
        $subcomments.prepend(data);
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
        install_voting_handlers($subcomments.children().first());
        install_comment_on_object_handler($subcomments.children().first());
        install_toggle_comment_handler($subcomments.children().first());
        var $fancybox = add_link.parents('.fancybox-data');
        if($fancybox && $fancybox.length > 0)
        {
            $(".fancybox-data").mCustomScrollbar("update");
        }

    });

    event.stopPropagation();
    event.preventDefault();
    return false;
};

var comment_radio_handler = function(event){
	var $text_element = $(this).parents('.radio_module').parent().find('.subcomment_text');
	if($text_element) {
        $text_element.parents('.subcomments_container').removeClass("hide");
		$text_element.focus();
    }

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

var install_review_handlers = function($parent_element) {
    install_delete_object_handler($parent_element);
    install_comment_on_object_handler($parent_element);
    if($parent_element) {
        $parent_element.find('.editReview').off('click', edit_review_handler ).on('click', edit_review_handler);
        $parent_element.find('.writeReview').on('click', write_review_handler).on('click', write_review_handler);
    }
    else {
        $('.editReview').off('click', edit_review_handler ).on('click', edit_review_handler);
        $('.writeReview').on('click', write_review_handler).on('click', write_review_handler);
    }

}

var install_comment_on_object_handler = function($parent_element) {
    if($parent_element)
    {
        $parent_element.find('.comment_on_object').off('submit', comment_on_object_handler).on('submit', comment_on_object_handler);
        $parent_element.find('.subcomment_text').off('keydown', comment_on_object_key_handler).on('keydown', comment_on_object_key_handler);
        $parent_element.find('.subcomment_text').autosize({append: "\n"});
        $parent_element.find('.viewPreviousComments').off('click', view_previous_comments_handler).on('click', view_previous_comments_handler);
        $parent_element.find('.comment_radio').off('click', comment_radio_handler).on('click', comment_radio_handler);
        
    }
    else
    {
        $('.comment_on_object').off('submit', comment_on_object_handler).on('submit', comment_on_object_handler);
        $('.subcomment_text').off('keydown', comment_on_object_key_handler).on('keydown', comment_on_object_key_handler);
        $('.subcomment_text').autosize({append: "\n"});
        $('.viewPreviousComments').off('click', view_previous_comments_handler).on('click', view_previous_comments_handler);
        $('.comment_radio').off('click', comment_radio_handler).on('click', comment_radio_handler);
    }
};