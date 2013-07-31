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
