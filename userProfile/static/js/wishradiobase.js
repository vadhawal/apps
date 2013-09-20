var login_required_handler = function()
{
    if(!is_authenticated)
    {
        var goto_url = login_url +'?next=' + window.location.pathname;
        document.location.href = goto_url; 
        return true;
    }
    return false;
}

var vendor_followers_handler = function(event) {
    event.preventDefault();
    $("<div id='pop_up'><span class='button b-close'><span>X</span></span></div>").appendTo("body").addClass('popup');
    $('#pop_up').bPopup({
        content:'ajax',
        loadUrl:$(this).attr("href"),
        zIndex: 2,
        onClose: function(){ $('#pop_up').remove(); },
        scrollBar:'true'
    },
    function() {
            install_follow_handlers();
    });
};

var FollowUnfollow = function($elementClicked, new_count) {
    var $element = $elementClicked.parent();
    var classes = $element.attr('class');
    if (classes.indexOf('following') == -1) {
        classes+= ' following';
    }
    else {
        classes = classes.replace('following', '');
    }
    $element.attr('class', classes); 
    var $followerCountElement = $("#" + $elementClicked.data("id"));
    if ($followerCountElement) {
        console.log($followerCountElement.html());
        var newHTML = new_count;
        $followerCountElement.html(newHTML);
    }
}

var follow_handler = function(event) {
    if(login_required_handler())
        return false;

    var $elementClicked = $(this);
    $elementClicked.off("click", follow_handler);
    var $followerCountElement = $("#" + $elementClicked.data("id"));
    var followerCount = $followerCountElement.html();
    followerCount = parseInt(followerCount) + 1;
    $followerCountElement.html(followerCount);
    var url =  $elementClicked.data("href");

    $.post(url, {}, function(data) {
        var return_val = JSON.parse(data)
        if (return_val.success  == true) {
            FollowUnfollow($elementClicked, return_val.count);
        } else {
            //showSnazzySuccessMessage("Something went wrong!");
        }
        $elementClicked.on("click", follow_handler);
    });
    event.stopPropagation();
    event.preventDefault();
    return false;
};

var unfollow_handler = function(event) {
    if(login_required_handler())
        return false;

    var $elementClicked = $(this);
    $elementClicked.off("click", unfollow_handler);
    var url =  $elementClicked.data("href");
    var $followerCountElement = $("#" + $elementClicked.data("id"));
    var followerCount = $followerCountElement.html();
    followerCount = parseInt(followerCount) - 1;
    $followerCountElement.html(followerCount);

    $.post(url, {}, function(data) {
        var return_val = JSON.parse(data)
        if (return_val.success  == true) {
            FollowUnfollow($elementClicked, return_val.count);
        } else {
            //showSnazzySuccessMessage("Something went wrong!");
        }
        $elementClicked.on("click", unfollow_handler);
    });
    event.stopPropagation();
    event.preventDefault();
    return false;
};

var install_follow_handlers = function() {
    $('.follow-btn').off("click").on("click", follow_handler);
    $('.unfollow-btn').off("click").on("click", unfollow_handler);
}

var sharewish_handler = function() {
    if(login_required_handler())
        return false;
    var $elementClicked = $(this);
    var link = $elementClicked.data("href");
    $.get(link, {}, function(data) {
    if(data == 'ok')
      alert('shared');
    });
    return false;
}

var share_store_handler = function(event) {
    if(login_required_handler())
        return false;
    
    var $elementClicked = $(this);
    var link =  $elementClicked.data("href");

    $.get(link, {}, function(data) {
        var obj_data = JSON.parse(data);
        if(obj_data.success == true)
          alert('shared');
    });
    event.stopPropagation();
    event.preventDefault();
    return false;
};

$(document).ready(function() {
    install_follow_handlers();
    $('.vendorFollowers').on("click", display_popup_handler);
    $('.shareaction').off("click").on("click", share_action_handler);
    $(".imgIframe").off("click").on("click", img_iframe_handler);
    $('.shareDeal').off("click").on('click', sharewish_handler);
    $('.share_store').off("click").on("click", share_store_handler);
    $('.store_sharers').off("click").on("click", display_popup_handler);
});

