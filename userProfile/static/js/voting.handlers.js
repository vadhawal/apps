var voting_handlers = function(event){
		var add_link = $(this);
		$.post(add_link.attr('href'),{HTTP_X_REQUESTED:'XMLHttpRequest'},
	       function(data) {
	           if (data.success == true) {
	               add_link.parent().find('a.pScore').text(data.score.num_up_votes);
	               if(add_link.hasClass('upvote'))
	               {
	               		add_link.removeClass('upvote').addClass('clearvote');
	               		add_link.text('Unlike');
	               		$newhref = add_link.attr('href').replace('up', 'clear');
	               		add_link.attr('href', $newhref);
	               }
	               else if(add_link.hasClass('clearvote'))
	               {
	               		add_link.removeClass('clearvote').addClass('upvote');
	               		add_link.text('Like');
	               		$newhref = add_link.attr('href').replace('clear', 'up');
	               		add_link.attr('href', $newhref);
	               }
	           } else {
	               alert('ERROR: ' + data.error_message);
	           }
	        }, 'json');
		event.stopPropagation();
		event.preventDefault();
		return false;  
};


