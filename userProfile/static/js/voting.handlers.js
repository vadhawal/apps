var voting_handlers = function(event){
		var add_link = $(this);
		$.post(add_link.attr('href'),{HTTP_X_REQUESTED:'XMLHttpRequest'},
	       function(data) {
	           if (data.success == true) {
	               add_link.parent().find('a.pScore').text(data.score.num_up_votes);
	               add_link.parent().find('span.nScore').text(data.score.num_down_votes);
	           } else {
	               alert('ERROR: ' + data.error_message);
	           }
	        }, 'json');
		event.stopPropagation();
		event.preventDefault();
		return false;  
};

var new_voting_handlers = function(event){
		var add_link = $(this);

		var prev_up = add_link.parent().find('a.pScore').text();
		var prev_down = add_link.parent().find('span.nScore').text();
		if($(this).hasClass('upvote'))
		{
			add_link.parent().find('a.pScore').text(parseInt(prev_up) + 1);
		}
		else if($(this).hasClass('downvote'))
		{
			
			add_link.parent().find('span.nScore').text(parseInt(prev_down) - 1);
		}
		else if($(this).hasClass('clearvote'))
		{
			prev_down = add_link.parent().find('span.nScore').text();
			add_link.parent().find('span.pScore').text(parseInt(prev_up) - 1);
		}
		$.post(add_link.attr('href'),{HTTP_X_REQUESTED:'XMLHttpRequest'},
	       function(data) {
	           if (data.success == true) {
	               //add_link.parent().find('a.pScore').text(data.score.num_up_votes);
	               //add_link.parent().find('span.nScore').text(data.score.num_down_votes);
	               /*
	               	pass
	               */
	           } else {
	               alert('ERROR: ' + data.error_message); //Debug
	           }
	        }, 'json');
		event.stopPropagation();
		event.preventDefault();
		return false;  
};

