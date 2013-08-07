var delete_album_handler = function(event) {
    var add_link = $(this);
    var link = add_link.attr('href');
    $.get(link, {}, function(data) {
        $('#vendorAlbum').html(data);
        install_album_handlers();
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
            install_album_handlers();
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
            install_album_handlers();
			$('a.thumb').each(function(){
        		$(this).lightBox();
    		});
        });
        event.stopPropagation();
        event.preventDefault();
        return false;
};

var upload_album_handler = function(event) {
    var add_link = $(this);
    var link = add_link.attr('href');
    $.get(link, {}, function(data) {
        $('#uploadOrCreate').html(data);
    });
    event.stopPropagation();
    event.preventDefault();
    return false;
};

var create_album_handler = function(event) {
    var add_link = $(this);
    var link = add_link.attr('href');
    $.get(link, {}, function(data) {
        $('#uploadOrCreate').html(data);
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
    $('.upload_album').off('click').on('click', upload_album_handler);
    $('.create_album').off('click').on('click', create_album_handler);
};