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
                if ($formParent.parents('.fancybox-data').length > 0) {
                    // isInsideFancyBox = true;
                    $formParent.find('.span5').removeClass('span5').addClass('span2');
                }
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

    var $url = $(this).data("href");
    var afterShowCallback = function() {
                                var $reviewFormContainer = $('.fancybox-inner').find('.review_on_object');
                                $reviewFormContainer.submit(review_submit_handler);

                                var value = parseInt($('[name="overall_value"]').val());
                                makeSlider($('.overall_value'), $('[name="overall_value"]'), value);

                                value = parseInt($('[name="price_value"]').val());
                                makeSlider($('.price_value'), $('[name="price_value"]') ,value);

                                value = parseInt($('[name="variety_value"]').val());
                                makeSlider($('.variety_value'), $('[name="variety_value"]'), value);

                                value = parseInt($('[name="quality_value"]').val())
                                makeSlider($('.quality_value'), $('[name="quality_value"]'), value);

                                value = parseInt($('[name="service_value"]').val())
                                makeSlider($('.service_value'), $('[name="service_value"]'), value);

                                value = parseInt($('[name="exchange_value"]').val())
                                makeSlider($('.exchange_value'), $('[name="exchange_value"]'), value);
                            };

    doOpenUrlWithAjaxFancyBox($url, afterShowCallback);
    return false;
};

var makeSlider = function($element, $serialize_to, start_val) {
    if(!start_val)
        start_val = 0;

    $element.noUiSlider({
         range: [0, 5]
        ,start: start_val
        ,step: 1
        ,handles: 1
        // ,serialization: {
        //      to: $serialize_to
        //     ,resolution: 1
        //     ,mark: ','
        // }
        ,slide: function(){
            var value = parseInt($(this).val());
            if(value === 0) {
                $serialize_to.val('');
            } else {
                $serialize_to.val(value);
            }
        }
    });  
}

var write_review_handler = function(event) {
	if(login_required_handler())
        return false;

    var $url = $(this).data("href");
    var afterShowCallback = function() {
                                var $reviewFormContainer = $('.fancybox-inner').find('.review_on_object');
                                $reviewFormContainer.submit(review_submit_handler);
                                makeSlider($('.overall_value'), $('[name="overall_value"]'), 0);
                                makeSlider($('.price_value'), $('[name="price_value"]'), 0);
                                makeSlider($('.variety_value'), $('[name="variety_value"]'), 0);
                                makeSlider($('.quality_value'), $('[name="quality_value"]'), 0);
                                makeSlider($('.service_value'), $('[name="service_value"]'), 0);
                                makeSlider($('.exchange_value'), $('[name="exchange_value"]'), 0);
                            };

    doOpenUrlWithAjaxFancyBox($url, afterShowCallback);
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
                    var subcomments_element = $("#comments").find('.reviewContainer');
                    $form.trigger('reset');
                    var $edit_review = $form.find('[name="edit_review"]');
                    if ($edit_review.length > 0) {
                        var element_id = $edit_review.data('element-id');
                        $('#'+element_id).replaceWith(ret_data.html);
                    } else {
                        subcomments_element.prepend(ret_data.html);                       
                    }
                    install_voting_handlers(subcomments_element);
                    install_toggle_comment_handler();
                    install_review_handlers(subcomments_element);
                    $form.find('.subcomment_text').trigger('autosize.resize');
                    $.fancybox.close();
                }
                else {
                    var errors = ret_data.errors;
                    $('.fancybox-inner').find('.error').removeClass('error');
                    $.each( errors, function( key, value ) {
                        var $element = $('.fancybox-inner').find('.' + key);
                        if ($element.length == 0) {
                            $('.fancybox-inner').find('[name="' + key + '"]').closest('.controls').find(".label_text").addClass('error');
                        } else {
                            $element.closest('.controls').find(".label_text").addClass('error');
                        }
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
        var $subcomments_container = add_link.closest('.subcomments_container');
        var $subcomments = $subcomments_container.find('.subcomments');
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
            var $prevCommentsTab = $subcomments_container.find('.viewPreviousComments');
            if ($prevCommentsTab) {
                var $prevCommentsParent = $prevCommentsTab.parent();
                if ($prevCommentsParent) {
                    var $parentNextSibling = $prevCommentsTab.parent().next();
                    if ($parentNextSibling.length > 0 && $parentNextSibling.prop('tagName').toLowerCase() === "hr") {
                        $parentNextSibling.remove();// remove the next HR
                    }
                    $prevCommentsParent.remove(); // remove the entire view previous comment tab
                }
            }
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
        $parent_element.find('.writeReview').off('click', write_review_handler).on('click', write_review_handler);
    }
    else {
        $('.editReview').off('click', edit_review_handler ).on('click', edit_review_handler);
        $('.writeReview').off('click', write_review_handler).on('click', write_review_handler);
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