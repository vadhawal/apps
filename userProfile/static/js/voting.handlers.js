var VOTING_STRING = {
	foundReviewHelpful: 'You found this review helpful.',
	foundReviewHelpfulQues: 'Was this review helpful?',
	like: 'Like',
	yes: 'Yes'
};

var display_popup_handler = function(event) {
	if($(this).html() === '(0)') {
		return false;
	}

	var $url = $(this).attr("href");
	var afterShowCallback = function() {
								install_follow_handlers();
								var $scrollContainer = $('.fancybox-inner').find('.scrollContainer');
								$scrollContainer.imagesLoaded({
            						complete: function(images) {
            							setupCustomScrollBar($scrollContainer);
								    }
								});
							};
    doOpenUrlWithAjaxFancyBox($url, afterShowCallback);
    return false;
};

var voting_handlers = function(event){
	    if(login_required_handler())
        	return false; 
		var $elementClicked = $(this);
		var url =  $elementClicked.data("href");
		$.post(url, {HTTP_X_REQUESTED:'XMLHttpRequest'},
	       function(data) {
	           if (data.success == true) {
	               $elementClicked.parent().parent().find('a.pScore').text('('+data.score.num_up_votes+')');
	               if($elementClicked.hasClass('upvote'))
	               {
	               		$elementClicked.removeClass('upvote').addClass('clearvote');
	               		$elementClicked.parent().children().first().text(VOTING_STRING.like);
	               		$elementClicked.parent().children().first().addClass('clearvote');
	               		$elementClicked.children().first().text("");
	               		$newhref = url.replace('up', 'clear');
	               		$elementClicked.data('href', $newhref);
	               }
	               else if($elementClicked.hasClass('clearvote'))
	               {
	               		$elementClicked.removeClass('clearvote').addClass('upvote');
	               		$elementClicked.children().first().text(VOTING_STRING.like);
	               		$elementClicked.parent().children().first().text("");
	               		$elementClicked.parent().children().first().removeClass('clearvote');
	               		$newhref = url.replace('clear', 'up');
	               		$elementClicked.data('href', $newhref);
	               }
	           } else {
	               alert('ERROR: ' + data.error_message);
	           }
	        }, 'json');
		event.stopPropagation();
		event.preventDefault();
		return false;  
};

var review_voting_handler = function(event){
		if(login_required_handler())
        	return false;
		var $elementClicked = $(this);
		var url =  $elementClicked.data("href");
		$.post(url, {HTTP_X_REQUESTED:'XMLHttpRequest'},
	       function(data) {
	           if (data.success == true) {
					var $parent = $elementClicked.parent(),
						removeClass = "",
						addClass = "",
						new_url = "",
						spanText = "",
						innerSpantText = "";
					$parent.find('a.pScore').text('(' + data.score.num_up_votes + ')');
					if($elementClicked.hasClass('found-helpful'))
					{
						new_url = url.replace('up', 'clear');
						spanText = VOTING_STRING.foundReviewHelpful;
						removeClass = 'found-helpful radioColorBackground';
						addClass = 'clear-helpful';
						innerSpantText = "";
					}
					else if($elementClicked.hasClass('clear-helpful'))
					{
						addClass = 'found-helpful radioColorBackground';
						removeClass = 'clear-helpful';
					 	new_url = url.replace('clear', 'up');
						spanText = VOTING_STRING.foundReviewHelpfulQues;
						innerSpantText = VOTING_STRING.yes;
					}
					$elementClicked.removeClass(removeClass);
					$elementClicked.addClass(addClass);
					$elementClicked.children().first().text(innerSpantText);
					$elementClicked.data("href", new_url);
					$parent.children('span').text(spanText);
					install_review_voting_handler($parent);
	           } else {
	               alert('ERROR: ' + data.error_message);
	           }
	        }, 'json');
		event.stopPropagation();
		event.preventDefault();
		return false;  
};
var install_voting_handlers = function($parent_element){
	if($parent_element)
	{
		$parent_element.find('a.upvote').off("click", voting_handlers).on("click", voting_handlers);
		$parent_element.find('a.downvote').off("click", voting_handlers).on("click", voting_handlers);
		$parent_element.find('a.clearvote').off("click", voting_handlers).on("click", voting_handlers);
		$parent_element.find('a.pScore').off("click", display_popup_handler).on("click", display_popup_handler);
		$parent_element.find('a.broadcasters').off("click", display_popup_handler).on("click", display_popup_handler);
	}
	else
	{
    	$('a.upvote').add('a.downvote').add('a.clearvote').off("click", voting_handlers).on("click", voting_handlers);
    	$('a.pScore').add('a.broadcasters').off("click", display_popup_handler).on("click", display_popup_handler);
    }
};
var install_review_voting_handler = function($parent_element) {
	if($parent_element)
	{
		$parent_element.find('.found-helpful').off("click", review_voting_handler).on("click", review_voting_handler);
		$parent_element.find('.clear-helpful').off("click", review_voting_handler).on("click", review_voting_handler);
	}
	else
	{
		$('.found-helpful').add('.clear-helpful').off("click", review_voting_handler).on("click", review_voting_handler);
	}
};