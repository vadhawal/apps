var delete_action_handler = function(event) {
    var add_link = $(this);
    var link = add_link.attr('href');
    $.get(link, {}, function(data) {
        if(data == 'ok')
          $('#action'+add_link.attr('data-action-id')).html("");
    });
    event.stopPropagation();
	event.preventDefault();
    return false;
};

var display_popup_handler = function(event) {
    var w = 700;
    var h = 500;
    var left = 100;
    var top = 100;
    var name="Friends";
    var settings = 'height=' + h + ',width=' + w + ',left=' + left + ',top=' + top + ',resizable=yes,scrollbars=yes,toolbar=no,menubar=no,location=yes,directories=no,status=yes';
    var url = $(this).attr("href");
    window.open(url, name, settings);
    event.stopPropagation();
	event.preventDefault();
    return false;
};

var share_action_handler = function(event) {
    var add_link = $(this);
    var link = add_link.attr('href');
    $.get(link, {}, function(data) {
        if(data == 'ok')
          alert('shared');
    });
   	event.stopPropagation();
	event.preventDefault();
    return false;
};