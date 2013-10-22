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
    if(login_required_handler())
        return false;
    var add_link = $(this);
    var link = add_link.attr('href');

    $("<div id='pop_up'><span class='button b-close'><span>X</span></span></div>").appendTo("body").addClass('popup');
    $('#pop_up').bPopup({
        content:'ajax',
        loadUrl:link,
        zIndex: 2,
        onClose: function(){ $('#pop_up').remove(); },
        scrollBar:'true',
        loadCallback: function(){
            $('.album-form').on('submit', album_form_submit_handler);
        }
    });

    event.stopPropagation();
    event.preventDefault();
    return false;
};

var album_form_submit_handler = function() {
    var $form = $(this);
    $.ajax({
        type: $form.attr('method'),
        url: $form.attr('action'),
        data: $form.serialize(),
        success: function (data) {
            var ret_data = JSON.parse(data);
            var url = ret_data.url;
            window.location.assign(url);
        },
        error: function(xhr) {
            var errors = JSON.parse(xhr.responseText);
            $('#pop_up').find('.error').removeClass('error');
            $.each( errors, function( key, value ) {
                $('#pop_up').find('[name="' + key + '"]').addClass('error');
            });
        }
    });
    return false;
}

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