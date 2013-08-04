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
    /*var w = 700;
    var h = 500;
    var left = 100;
    var top = 100;
    var name="Friends";
    var settings = 'height=' + h + ',width=' + w + ',left=' + left + ',top=' + top + ',resizable=yes,scrollbars=yes,toolbar=no,menubar=no,location=yes,directories=no,status=yes';
    var url = $(this).attr("href");
    window.open(url, name, settings);
    event.stopPropagation();
	event.preventDefault();
    return false;*/

    event.preventDefault();
    $("<div id='pop_up'><span class='button b-close'><span>X</span></span></div>").appendTo("body").addClass('popup');
    $('#pop_up').bPopup({
        content:'ajax',
        loadUrl:$(this).attr("href"),
        zIndex: 2,
        onClose: function(){ $('#pop_up').remove(); },
        scrollBar:'true'
    });
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

var follow_post_handler = function(event) {
    var add_link = $(this);
    var link = add_link.attr('href');
    $.get(link, {}, function(data) {
        if(data == 'ok')
        {
          $href = add_link.attr('href')
          $newhref = $href.replace("follow", "unfollow");
          add_link.attr('href', $newhref);
          add_link.html("unfollow post");
        }
    });
    event.stopPropagation();
    event.preventDefault();
    return false;
};

var unfollow_post_handler = function(event) {
    var add_link = $(this);
    var link = add_link.attr('href');
    $.get(link, {}, function(data) {
        if(data == 'ok')
        {
          $href = add_link.attr('href')
          $newhref = $href.replace("unfollow", "follow");
          add_link.attr('href', $newhref);
          add_link.html("follow post");
        }
    });
    event.stopPropagation();
    event.preventDefault();
    return false;
};

var img_iframe_handler =  function(){
    var oldId = $(this).attr("id");
    var currentId = oldId.substring(3);
    pTP = "pTP"+currentId;
    pDP = "pDP"+currentId;
    oldId = "#"+oldId;
    currentId = "#"+currentId;
    $(oldId).css({'display': 'none'});
    $(currentId).css({'display': 'block'});
    $('#'+pTP).css({'width': '495px'});
    $('#'+pDP).css({'width': '495px'});
};

var install_action_handlers = function(){
    install_voting_handlers();
    $('.deleteAction').off("click").on("click", delete_action_handler);
    $('.shareaction').off("click").on("click", share_action_handler);
    $('.followpost').off("click").on("click", follow_post_handler);
    $('.unfollowpost').off("click").on("click", unfollow_post_handler);
    $('a.thumb').each(function(){
        $(this).lightBox();
    });
    $('a.album_in_feed').each(function(){
        $(this).lightBox();
    });
    $(".imgIframe").off("click").on("click", img_iframe_handler);
    $('.previewPosted').width('100%');
}

var install_voting_handlers = function(){
    $('.upvote').add('.downvote').add('.clearvote').off("click").on("click", voting_handlers);
    $('.pScore').add('.broadcasters').off("click").on("click", display_popup_handler);
}
