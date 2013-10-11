var display_popup_handler = function(event) {
    /*var w = 700;
    var h = 500;
    var left = 100;
    var top = 100;
    var name="Friends";
    var settings = 'height=' + h + ',width=' + w + ',left=' + left + ',top=' + top + ',resizable=yes,scrollbars=yes,toolbar=no,menubar=no,location=yes,directories=no,status=yes';
    var url = $(this).attr("href");
    window.open(url, name, settings);
    event.stopPropagation();
	event.preventDefault();
    return false;*/

    event.preventDefault();
    $("<div id='pop_up'><span class='button b-close'><span>X</span></span></div>").appendTo("body").addClass('popup');
    $('#pop_up').bPopup({
        content:'ajax',
        loadUrl:$(this).attr("href"),
        zIndex: 8050,
        onClose: function(){ $('#pop_up').remove(); },
        scrollBar:'true'
    },
    function() {
            install_follow_handlers();
    });
    
};

var voting_handlers = function(event){
	    if(login_required_handler())
        	return false; 
		var $elementClicked = $(this);
		var url =  $elementClicked.data("href");
		$.post(url, {HTTP_X_REQUESTED:'XMLHttpRequest'},
	       function(data) {
	           if (data.success == true) {
	               $elementClicked.parent().find('a.pScore').text('('+data.score.num_up_votes+')');
	               if($elementClicked.hasClass('upvote'))
	               {
	               		$elementClicked.removeClass('upvote').addClass('clearvote');
	               		$elementClicked.text('Unlike');
	               		$newhref = url.replace('up', 'clear');
	               		$elementClicked.data('href', $newhref);
	               }
	               else if($elementClicked.hasClass('clearvote'))
	               {
	               		$elementClicked.removeClass('clearvote').addClass('upvote');
	               		$elementClicked.text('Like');
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
	               $elementClicked.parent().find('a.pScore').text(data.score.num_up_votes);
	               if($elementClicked.hasClass('found-helpful'))
	               {
	               		var new_url = url.replace('up', 'clear');
	               		var html = '</span>You found this review helpful.</span><a class="clear-helpful" href="'+new_url+'">Clear</a>';
	               		$elementClicked.parent().html(html);
	               }
	               else if($elementClicked.hasClass('not-found-helpful'))
	               {
	               		var new_url = url.replace('down', 'clear');
	               		var html = '</span>You did not find this review helpful!</span><a class="clear-helpful" href="'+new_url+'">Clear</a>';
	               		$elementClicked.parent().html(html);
	               }
	               else if($elementClicked.hasClass('clear-helpful'))
	               {
	               		var up_url = url.replace('clear', 'up');
	               		var down_url = url.replace('clear', 'down');
	               		var html = '<span>Do you find this review helpful? </span><a class="found-helpful" href="'+up_url+'">Yes </a>'+
                        '<a class="not-found-helpful" href="'+down_url+'">No</a>';
                        $elementClicked.parent().html(html);
	               }
	               install_voting_handlers();
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
		$parent_element.find('.upvote').off("click", voting_handlers).on("click", voting_handlers);
		$parent_element.find('.downvote').off("click", voting_handlers).on("click", voting_handlers);
		$parent_element.find('.clearvote').off("click", voting_handlers).on("click", voting_handlers);
		$parent_element.find('.pScore').off("click", display_popup_handler).on("click", display_popup_handler);
		$parent_element.find('.broadcasters').off("click", display_popup_handler).on("click", display_popup_handler);
	}
	else
	{
    	$('.upvote').add('.downvote').add('.clearvote').off("click", voting_handlers).on("click", voting_handlers);
    	$('.pScore').add('.broadcasters').off("click", display_popup_handler).on("click", display_popup_handler);
    }
}

var install_review_voting_handler = function($parent_element) {
	if($parent_element)
	{
		$parent_element.find('.found-helpful').off("click", review_voting_handler).on("click", review_voting_handler);
		$parent_element.find('.not-found-helpful').off("click", review_voting_handler).on("click", review_voting_handler);
		$parent_element.find('.clear-helpful').off("click", review_voting_handler).on("click", review_voting_handler);
	}
	else
	{
		$('.found-helpful').add('.not-found-helpful').add('.clear-helpful').off("click", review_voting_handler).on("click", review_voting_handler);
	}
}

