var voting_handlers = function(event){
	    if(login_required_handler())
        	return false; 
		var $elementClicked = $(this);
		var url =  $elementClicked.data("href");
		$.post(url, {HTTP_X_REQUESTED:'XMLHttpRequest'},
	       function(data) {
	           if (data.success == true) {
	               $elementClicked.parent().find('a.pScore').text(data.score.num_up_votes);
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


