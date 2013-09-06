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

var review_voting_handler = function(event){
		var add_link = $(this);
		$.post(add_link.attr('href'),{HTTP_X_REQUESTED:'XMLHttpRequest'},
	       function(data) {
	           if (data.success == true) {
	               add_link.parent().find('a.pScore').text(data.score.num_up_votes);
	               if(add_link.hasClass('found-helpful'))
	               {
	               		var url = add_link.attr('href');
	               		var new_url = url.replace('up', 'clear');
	               		var html = '</span>You found this review helpful.</span><a class="clear-helpful" href="'+new_url+'">Clear</a>';
	               		add_link.parent().html(html);
	               }
	               else if(add_link.hasClass('not-found-helpful'))
	               {
	               		var url = add_link.attr('href');
	               		var new_url = url.replace('down', 'clear');
	               		var html = '</span>You did not find this review helpful!</span><a class="clear-helpful" href="'+new_url+'">Clear</a>';
	               		add_link.parent().html(html);
	               }
	               else if(add_link.hasClass('clear-helpful'))
	               {
	               		var url = add_link.attr('href');
	               		var up_url = url.replace('clear', 'up');
	               		var down_url = url.replace('clear', 'down');
	               		var html = '<span>Do you find this review helpful? </span><a class="found-helpful" href="'+up_url+'">Yes </a>'+
                        '<a class="not-found-helpful" href="'+down_url+'">No</a>';
                        add_link.parent().html(html);
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


