var delete_album_handler = function(event) {
    var add_link = $(this);
    var link = add_link.attr('href');
    $.get(link, {}, function(data) {
        $('#vendorAlbum').html(data);
        install_album_handlers($('#vendorAlbum'));
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
            install_album_handlers($('#vendorAlbum'));
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
            install_album_handlers($('#vendorAlbum'));
			$('a.thumb').each(function(){
        		$(this).fancybox({
                        scrolling: 'yes',
                        minWidth:800,
                        minHeight:600,
                        autoSize: true,
                        helpers : { overlay : { locked : false } }
                });
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

var install_album_handlers = function($parent_element){
	install_voting_handlers($parent_element);  //Assumed inheritance from action.handler.js
    if($parent_element)
    {
    	$parent_element.find('.delete_album').off('click').on('click', delete_album_handler);
    	$parent_element.find('.back_to_album').off('click').on('click', back_to_album_handler);
    	//$('.album_photos').off('click').on('click', show_album_handler);  //disabling the ajax for now. will land to dedicated page instead.
        $parent_element.find('.upload_album').off('click').on('click', upload_album_handler);
        $parent_element.find('.create_album').off('click').on('click', create_album_handler);
    }
    else
    {
        $('.delete_album').off('click').on('click', delete_album_handler);
        $('.back_to_album').off('click').on('click', back_to_album_handler);
        //$('.album_photos').off('click').on('click', show_album_handler);  //disabling the ajax for now. will land to dedicated page instead.
        $('.upload_album').off('click').on('click', upload_album_handler);
        $('.create_album').off('click').on('click', create_album_handler);        
    }
};