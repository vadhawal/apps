var vendor_followers_handler = function(event) {
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

var FollowUnfollow = function($elementClicked, added) {
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
        var followerCount = $followerCountElement.html();
        followerCount = added ? parseInt(followerCount) + 1 : parseInt(followerCount) - 1;
        var newHTML = followerCount;
        $followerCountElement.html(newHTML);
    }
}

var follow_handler = function(event) {
    var $add_link = $(this);
    FollowUnfollow($add_link, true);
    $.post($add_link.attr('href'), {}, function(data) {
        if (data  == 'ok') {
        } else {
            //showSnazzySuccessMessage("Something went wrong!");
        }
    });
    event.stopPropagation();
    event.preventDefault();
    return false;
};

var unfollow_handler = function(event) {
        var $add_link = $(this);
        FollowUnfollow($add_link, false);
        $.post($add_link.attr('href'), {}, function(data) {
            if (data == 'ok') {
            } else {
                //showSnazzySuccessMessage("Something went wrong!");
            }
    });
    event.stopPropagation();
    event.preventDefault();
    return false;
};

var install_follow_handlers = function() {
    $('.follow-btn').off("click").on("click", follow_handler);
    $('.unfollow-btn').off("click").on("click", unfollow_handler);
}
$(document).ready(function() {
	install_follow_handlers();
	$('.vendorFollowers').on("click", vendor_followers_handler);
});

