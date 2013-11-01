(function($) {
    $.fn.imagesLoaded = function(options) {
        var images = this.find("img"), 
            loadedImages = [], 
            options = options;

        images.each(function(i, image) {
            function loaded() {
                loadedImages.push(this);
                if(options.imageLoaded) {
                    options.imageLoaded(this);    
                }
                if(loadedImages.length == images.length) {
                    if(options.complete) {
                        options.complete(loadedImages);    
                    }
                }
            }

            if(image.complete || image.complete === undefined) {
                // Image is already loaded
                loaded.call(image);               
            } else {
                // Image is not loaded yet, bind event
                $(image).load(loaded);
            }
        });
    }
})(jQuery);

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
        var newHTML = "("+new_count+")";
        $followerCountElement.text(newHTML);
    }
}

var follow_handler = function(event) {
    if(login_required_handler())
        return false;

    var $elementClicked = $(this);
    $elementClicked.off("click", follow_handler);
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

    $.post(url, {}, function(data) {
        var return_val = JSON.parse(data);
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
    $('.follow-btn').off("click", follow_handler).on("click", follow_handler);
    $('.unfollow-btn').off("click", unfollow_handler).on("click", unfollow_handler);
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

var share_object_handler = function(event) {
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

var delete_object_handler = function(event) {
    if(login_required_handler())
        return false;
    
    var $elementClicked = $(this);
    var link =  $elementClicked.data("href");

    $.get(link, {}, function(data) {
        var dataResult = JSON.parse(data);
        if(dataResult.success == true) {
             alert('object deleted');
        }
        else {
            if(dataResult.error_codes.indexOf(400) != -1) {
                alert('Unauthorized Action!')
            }
            else if(dataResult.error_codes.indexOf(401) != -1) {
                alert('Object Does Not Exist!')
            }
            else if(dataResult.error_codes.indexOf(402) != -1) {
                alert('Only supported through Ajax!');
            }
        }
    });
    event.stopPropagation();
    event.preventDefault();
    return false;    
}

var install_delete_object_handler = function($parent_element) {
    if($parent_element) {
        $parent_element.find('.deleteObject').off('click', delete_object_handler).on('click', delete_object_handler);
    }
    else {
        $('.deleteObject').off('click', delete_object_handler).on('click', delete_object_handler);
    }
}

var install_share_object_handler =  function($parent_element) {
    if($parent_element) {
        $parent_element.find('.shareObject').off('click', share_object_handler).on('click', share_object_handler);
    }
    else {
        $('.shareObject').off('click', share_object_handler).on('click', share_object_handler);
    }
}

var doOpenUrlInFancyBox = function(url) {
    $("<a href='"+url +"'></a>").appendTo("body").addClass('cropImageFancyBox');
    $('a.cropImageFancyBox').fancybox({
        'frameWidth'    :       500,
        'frameHeight'   :       500,
        'hideOnContentClick': false, 
        'type':'iframe',
         onClosed: function(){
            $('a.cropImageFancyBox').remove();
         }
    }); 
    $('a.cropImageFancyBox').click();
}

$(document).ready(function() {
    install_follow_handlers();
    $('.vendorFollowers').on("click", display_popup_handler);
    $('.shareaction').off("click", share_action_handler).on("click", share_action_handler);
    $(".imgIframe").off("click", img_iframe_handler).on("click", img_iframe_handler);
    $('.shareDeal').off("click", sharewish_handler).on('click', sharewish_handler);
    $('.share_store').off("click", share_store_handler).on("click", share_store_handler);
    $('.store_sharers').off("click", display_popup_handler).on("click", display_popup_handler);
    install_share_object_handler();
    install_delete_object_handler();
    $('a.wishimg-deal-homepage').fancybox({
        scrolling: 'yes',
        minWidth: 500,
        minHeight: 450,
        autoSize: true,
        helpers : { overlay : { locked : false } }
    });
});

