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

var share_action_handler = function(event) {
    if(login_required_handler())
        return false;
    
    var $elementClicked = $(this);
    var link =  $elementClicked.data("href");

    $.get(link, {}, function(data) {
        var dataResult = JSON.parse(data);
        if(dataResult.success == true) {
             $elementClicked.text("Shared");
             var $shareCountEle = $elementClicked.parent().find('.sharedCount');
             var shareCount = dataResult.count;
             $shareCountEle.text("(" + shareCount + ")");
        }
    });
   	event.stopPropagation();
	event.preventDefault();
    return false;
};

var follow_post_handler = function(event) {
    if(login_required_handler())
        return false;
    
    var $elementClicked = $(this);
    var link =  $elementClicked.data("href");

    $.get(link, {}, function(data) {
        var dataResult = JSON.parse(data);
        if(dataResult.success == true)
        {
          $href = $elementClicked.attr('href');
          $newhref = $href.replace("follow", "unfollow");
          $elementClicked.attr('href', $newhref);
          $elementClicked.html("unfollow post");
        }
    });
    event.stopPropagation();
    event.preventDefault();
    return false;
};

var unfollow_post_handler = function(event) {
    if(login_required_handler())
        return false;
    
    var $elementClicked = $(this);
    var link =  $elementClicked.data("href");
    
    $.get(link, {}, function(data) {
        var dataResult = JSON.parse(data);
        if(dataResult.success == true)
        {
          $href = $elementClicked.attr('href')
          $newhref = $href.replace("unfollow", "follow");
          $elementClicked.attr('href', $newhref);
          $elementClicked.html("follow post");
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

var install_action_handlers = function($parent_element){
    install_voting_handlers($parent_element);
    install_toggle_comment_handler($parent_element); //inherited from comment.handlers.js
    install_comment_on_object_handler($parent_element);
    if($parent_element)
    {
	    $parent_element.find('.deleteAction').off("click", delete_action_handler).on("click", delete_action_handler);
	    $parent_element.find('.shareaction').off("click", share_action_handler).on("click", share_action_handler);
	    $parent_element.find('.shareObject').off("click", share_object_handler).on("click", share_object_handler);
	    $parent_element.find('.followpost').off("click", follow_post_handler).on("click", follow_post_handler);
	    $parent_element.find('.unfollowpost').off("click", unfollow_post_handler).on("click", unfollow_post_handler);
	    $parent_element.find('a.album_in_feed').off('click').on('click', album_in_feed_handler);
	    $parent_element.find(".imgIframe").off("click", album_in_feed_handler).on("click", img_iframe_handler);
	    $parent_element.find('.previewPosted').width('100%');
	}
	else
	{
	    $('.deleteAction').off("click", delete_action_handler).on("click", delete_action_handler);
	    $('.shareaction').off("click", share_action_handler).on("click", share_action_handler);
	    $('.shareObject').off("click", share_object_handler).on("click", share_object_handler);
	    $('.followpost').off("click", follow_post_handler).on("click", follow_post_handler);
	    $('.unfollowpost').off("click", unfollow_post_handler).on("click", unfollow_post_handler);
	    $('a.album_in_feed').off('click').on('click', album_in_feed_handler);
	    $(".imgIframe").off("click", album_in_feed_handler).on("click", img_iframe_handler);
	    $('.previewPosted').width('100%');		
	}
}

var album_in_feed_handler = function(){
    var $element_clicked = $(this);
    var album_url = $element_clicked.data("album-url");
    $.get(album_url, {}, function(data) {
        $element_clicked.closest('div.album-feed-container').append(data);
        
        var elements = $element_clicked.closest('div.album-feed-container').find('a.album_in_feed'); 
        elements.off('click');
        $(elements.get()).fancybox({
            scrolling: 'yes',
            minWidth:500,
            minHeight:450,
            autoSize: true,
            helpers : { overlay : { locked : false } }
        });
        $element_clicked.click();
    });
    return false;    
}

$(document).ready(function(){
    install_voting_handlers();  
});

