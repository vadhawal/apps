$(function() {
            $.ajaxSetup({
                 beforeSend: function(xhr, settings) {
                     function getCookie(name) {
                         var cookieValue = null;
                         if (document.cookie && document.cookie != '') {
                             var cookies = document.cookie.split(';');
                             for (var i = 0; i < cookies.length; i++) {
                                 var cookie = jQuery.trim(cookies[i]);
                                 // Does this cookie string begin with the name we want?
                             if (cookie.substring(0, name.length + 1) == (name + '=')) {
                                 cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                                 break;
                             }
                         }
                     }
                     return cookieValue;
                     }
                     if (!(/^http:.*/.test(settings.url) || /^https:.*/.test(settings.url))) {
                         // Only send the token to relative URLs i.e. locally.
                         xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
                     }
                 }
            });     
    });

$(document).ready(function() {

    $('.vendorFollowers').click(function() {
        var w = 700;
        var h = 500;
        var left = 100;
        var top = 100;
        var name="Friends";
        var settings = 'height=' + h + ',width=' + w + ',left=' + left + ',top=' + top + ',resizable=yes,scrollbars=yes,toolbar=no,menubar=no,location=yes,directories=no,status=yes';
        var url = $(this).attr("href");
        window.open(url, name, settings);

        return false;
    });

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
            followerCount = added ? parseInt(followerCount) + 1 : parseInt(followerCount) - 1;;
            var newHTML = (followerCount == 1) ? followerCount + " Follower" : followerCount + " Followers";
            $followerCountElement.html(newHTML);
        }
    }

    $('.follow-btn').click(function() {
        var $add_link = $(this);
        FollowUnfollow($add_link, true);
        $.post($add_link.attr('href'), {}, function(data) {
            if (data  == 'ok') {
            } else {
                //showSnazzySuccessMessage("Something went wrong!");
            }
        });
        return false;
    });

    $('.unfollow-btn').click(function() {
        var $add_link = $(this);
        FollowUnfollow($add_link, false);
        $.post($add_link.attr('href'), {}, function(data) {
            if (data == 'ok') {
            } else {
                //showSnazzySuccessMessage("Something went wrong!");
            }
        });
        return false;
    });
});