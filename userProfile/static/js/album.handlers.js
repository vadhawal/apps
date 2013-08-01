var delete_album_handler = function(event) {
    var add_link = $(this);
    var link = add_link.attr('href');
    $.get(link, {}, function(data) {
        $('#vendorAlbum').html(data);
    });
    event.stopPropagation();
    event.preventDefault();
    return false;
}; 

var back_to_album_handler = function(event) {
        var add_link = $(this);
        $('#vendorAlbum').html("");
        var link = add_link.attr('href');
        $.get(link, {}, function(data) {
            $('#vendorAlbum').html(data);
        });
        event.stopPropagation();
		event.preventDefault();
        return false;
};

var show_album_handler = function(event) {
        var add_link = $(this);
        var link = add_link.attr('href');
        $.get(link, {}, function(data) {
            $('#vendorAlbum').html(data);
            install_voting_handlers();  //Assumed inheritance from action.handler.js
			$('.delete_album').off('click').on('click', delete_album_handler);
			$('.back_to_album').off('click').on('click', back_to_album_handler);
			$('a.thumb').each(function(){
        		$(this).lightBox();
    		});
        });
        event.stopPropagation();
        event.preventDefault();
        return false;
};

var install_album_handlers = function(){
	install_voting_handlers();  //Assumed inheritance from action.handler.js
	$('.delete_album').off('click').on('click', delete_album_handler);
	$('.back_to_album').off('click').on('click', back_to_album_handler);
	$('.album_photos').off('click').on('click', show_album_handler);
};