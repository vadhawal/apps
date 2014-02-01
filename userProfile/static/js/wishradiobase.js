(function($) {
    $.fn.imagesLoaded = function(options) {
        var images = this.find("img"), 
            loadedImages = [], 
            options = options;

        if(images.length === 0)
            options.complete();
        
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

var openLoginForm = function($url) {
    var afterShowCallback = function() {
                                var $accountFormContainer = $('.fancybox-inner').find('.accountForm');
                                if($accountFormContainer.length > 0) {
                                    $accountFormContainer.on('submit', {action_url: $url}, account_form_submit_handler);
                                }
                            };

    doOpenUrlWithAjaxFancyBox($url, afterShowCallback);
    return false;
};

var login_required_handler = function()
{
    if(!is_authenticated)
    {
        var goto_url = login_url +'?next=' + window.location.pathname;
        openLoginForm(goto_url);
        return true;
    }
    return false;
};

var FollowUnfollow = function($elementClicked, new_count) {
    var $element = $elementClicked.parent();
    var classes = $element.attr('class');
    var follow = false;
    if (classes.indexOf('following') == -1) {
        classes += ' following';
        follow = true;
    }
    else {
        classes = classes.replace('following', '');
    }
    $element.attr('class', classes);
    var $followerCountElement;
    var $accordionContent = $elementClicked.parents('.accordion-content');
    if($accordionContent.length > 0) {
        var $accordionHeader = $accordionContent.prev();
        if($accordionHeader) {
            $followerCountElement = $accordionHeader.find('.objectCount');
            if ($followerCountElement && $followerCountElement.length > 0) {
                var prevCount = $followerCountElement.html();
                var newHTML = prevCount;
                if(follow === true) {
                    newHTML = parseInt(prevCount) + 1;
                } else {
                    if(parseInt(prevCount) > 0)
                        newHTML = parseInt(prevCount) - 1;
                }
                $followerCountElement.text(newHTML);
            }
        }
    } else {
        $followerCountElement = $elementClicked.parent().parent().find('.vendorFollowers');
        if ($followerCountElement && $followerCountElement.length > 0) {
            var newHTML = "("+new_count+")";
            $followerCountElement.text(newHTML);
        }
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
    /* data-object-type should be set for the objects having deleteObject class applied.
     * Using this we determine the object type to be shown in the confirmation message.
     */
    var object_type =  $elementClicked.data("object-type");

    $.confirm({
        text: "Are you sure you want to delete this " + object_type+ " ?",
        confirm: function(button) {
            $.get(link, {}, function(data) {
                var dataResult = JSON.parse(data);
                if(dataResult.success == true) {
                    /* Class objectToBeDeleted must be applied to the topmost element */
                    var $objectToBeDeleted = $elementClicked.parents('.objectToBeDeleted'); 
                    var $accordionContent = $objectToBeDeleted.parents('.accordion-content');
                    if($objectToBeDeleted.length > 0) {
                        if (object_type === "activity") {
                            var $seperator = $objectToBeDeleted.next();
                            if( $seperator.hasClass('dottedSeparator') ) {
                                $seperator.remove();
                            }
                            $objectToBeDeleted.remove();
                        } else {
                            $objectToBeDeleted.remove();
                        }
                        var $countElement;
                        if($accordionContent.length > 0) {
                            var $accordionHeader = $accordionContent.prev();
                            if($accordionHeader) {
                                $countElement = $accordionHeader.find('.objectCount');
                            }
                        }
                        if($countElement && $countElement.length > 0) {
                            var prevCount = $countElement.html();
                            var newCount = parseInt(prevCount) - 1;
                            $countElement.html(newCount);
                        }
                    } else {
                        console.log("Object is deleted silently");
                    }
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
        },
        cancel: function(button) {
            // do something
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

var doOpenUrlWithIframeFancyBox = function(url) {
    $.fancybox({
        'frameWidth'        :  500,
        'frameHeight'       :  500,
        'scrolling'         : 'no',
        'hideOnContentClick': false, 	
        'type'              :'iframe',
        'iframe'            : {'scrolling': 'no'},
         helpers            : { overlay : { locked : false } },
         afterClose           : function(){
                                  
                                },
        href				: url
    });

    return false;
}

var doOpenUrlWithAjaxFancyBox = function(url, afterShowCallback, scroll, afterCloseCallback) {
    var doScroll = 'no';
    var afterCloseCallbackImpl = function() { };
    if (typeof scroll !== "undefined") {
        doScroll = scroll;
    }
    if (typeof afterCloseCallback !== "undefined" && typeof afterCloseCallback === "function") {
        afterCloseCallbackImpl = afterCloseCallback;
    }
    $.fancybox({
        width               : 500,
        autoSize            : true,
        hideOnContentClick  : false,
        openEffect          : 'fade',
        closeEffect         : 'fade',
        type                :'ajax',
        helpers             : { overlay : { locked : false } },
        scrolling           : doScroll,
        href				: url,
        afterShow           : function() {
                                    if(typeof afterShowCallback !== 'undefined' && typeof afterShowCallback === "function")
                                        afterShowCallback();
                              },
        afterClose          : afterCloseCallbackImpl
        //,                
        // ajax                :   {
        //                             complete    : function(jqXHR, textStatus) {
        //                             if(typeof afterShowCallback !== 'undefined')
        //                                 afterShowCallback();
        //                         }
        // },
    });

    return false; 
}

var login_handler = function(event) {    
    var $url = $(this).attr("href");
    // var afterShowCallback = function() {
    //                             var $accountFormContainer = $('.fancybox-inner').find('.accountForm');
    //                             if($accountFormContainer.length > 0) {
    //                                 $accountFormContainer.on('submit', {action_url: $url}, account_form_submit_handler);
    //                             }
    //                         };

    // doOpenUrlWithAjaxFancyBox($url, afterShowCallback);
    openLoginForm($url);
    event.stopPropagation();
    event.preventDefault();
    return false;
};

var account_form_submit_handler = function(event) {
    var $form = $(this);
    var $action_url = event.data.action_url;
    $('.fancybox-inner').find('.error').remove();
    $('.fancybox-inner img.loader').removeClass("hide");
    $('.fancybox-inner .loginSubmit').addClass("hide");
    $.ajax({
        type: $form.attr('method'),
        url: $action_url,
        data: $form.serialize(),
        success: function (data) {
            var ret_data = JSON.parse(data);
            if(ret_data.success === true) {
                $.fancybox.close();
                var url = ret_data.url;
                window.location.assign(url);
            } else {
                var $errors = ret_data.errors.__all__;
                var $albumFormContainer = $('.fancybox-inner').find('.accountForm');
                $albumFormContainer.find('.errorColor').remove();
                $('<div/>', {
                    'class':'errorColor',
                    'html':'<span class="fontSize11" style="margin-left:20px;">'+$errors+'</span>'
                }).appendTo($albumFormContainer);
                $('.fancybox-inner img.loader').addClass("hide");
                $('.fancybox-inner .loginSubmit').removeClass("hide");
                $.fancybox.update();
            }
        },
        error: function(xhr) {
            var errors = JSON.parse(xhr.responseText);
            $('.fancybox-inner').find('.error').removeClass('error');
            $.each( errors, function( key, value ) {
                $('.fancybox-inner').find('[name="' + key + '"]').addClass('error');
            });
            $('.fancybox-inner img.loader').addClass("hide");
            $('.fancybox-inner .loginSubmit').removeClass("hide");
        }
    });
    return false;
};

function getParameters () {
    var prmstr = window.location.search.substr(1);
    var prmarr = prmstr.split ("&");
    var params = {};

    prmarr = prmarr.filter(function(value) {
        return value !== "" && value !== null;
    });

    for ( var i = 0; i < prmarr.length; i++) {
        var tmparr = prmarr[i].split("=");
        params[tmparr[0]] = tmparr[1];
    }

    return params;
}

var update_url = function (query_params, navigate) {
    var location = window.location;
    var baseUrl = location.protocol + '//' + location.host + location.pathname;
    var params = '';
    if(!$.isEmptyObject(query_params))
    {   
        params = '?';
        for(param in query_params) {
            params += param + '=' + query_params[param] + '&';
        }
        if(params.charAt(params.length - 1) === '&') {
            params = params.slice(0, -1);
        }
    }
    var newUrl = baseUrl + params;

    if(navigate) {
        document.location.href = newUrl;
    } else {
        window.history.pushState('','',newUrl);
    }
}

var suggest_store_handler = function(event) {
    var $elementClicked = $(this);
    $elementClicked.addClass('opened');
    var $url =  $elementClicked.data("href");
    var afterShowCallback = function() {
                                var $suggestFormContainer = $('.fancybox-inner').find('.suggestForm');
                                if($suggestFormContainer.length > 0) {
                                    $suggestFormContainer.on('submit', {action_url: $url}, suggest_form_submit_handler);
                                }
                            };
    var afterCloseCallback = function () {
        $('.suggestStore').removeClass('opened');
    }

    doOpenUrlWithAjaxFancyBox($url, afterShowCallback, 'no', afterCloseCallback);
    return false;  
}

var contact_us_handler = function(event) {
    var $elementClicked = $(this);
    $elementClicked.addClass('opened');
    var $url =  $elementClicked.data("href");
    var afterShowCallback = function() {
                                var $suggestFormContainer = $('.fancybox-inner').find('.contactForm');
                                if($suggestFormContainer.length > 0) {
                                    $suggestFormContainer.on('submit', {action_url: $url}, suggest_form_submit_handler);
                                }
                            };
    var afterCloseCallback = function () {
        $('.contactUs').removeClass('opened');
    }

    doOpenUrlWithAjaxFancyBox($url, afterShowCallback, 'no', afterCloseCallback);
    return false;  
}

var suggest_form_submit_handler = function(event) {
    var $form = $(this);
    var $action_url = event.data.action_url;
    $('.fancybox-inner img.loader').removeClass("hide");
    $('.fancybox-inner input[type=submit]').addClass("hide");
    $('.fancybox-inner').find('.error').removeClass("error");
    $.ajax({
        type: $form.attr('method'),
        url: $action_url,
        data: $form.serialize(),
        success: function (data) {
            if(data.success === true) {
                $form.hide();
                var $messageBox = $('.fancybox-inner').find('.message');
                $messageBox.removeClass('hide');
                $('.fancybox-inner').find('.suggestFormPrefix').hide(); 
                setTimeout(function() {
                    $.fancybox.close();
                }, 3000);
            }
            if($('.suggestStore').hasClass('opened')) {
                $('.suggestStore').removeClass('opened');
            }
            if($('.contactUs').hasClass('opened')) {
                $('.contactUs').removeClass('opened');
            }
            $('.fancybox-inner img.loader').addClass("hide");
            $('.fancybox-inner input[type=submit]').removeClass("hide");
        },
        error: function(xhr) {
            var errors = JSON.parse(xhr.responseText);
            $('.fancybox-inner').find('.error').removeClass('error');
            $.each( errors, function( key, value ) {
                $('.fancybox-inner').find('[name="' + key + '"]').addClass('error');
            });
            $('.fancybox-inner img.loader').addClass("hide");
            $('.fancybox-inner input[type=submit]').removeClass("hide");
        }
    });
    return false;
};

$(document).ready(function() {
    install_follow_handlers();
    $('.vendorFollowers').on("click", display_popup_handler);
    $('.followerCountBox').on("click", display_popup_handler);
    $('.shareaction').off("click", share_action_handler).on("click", share_action_handler);
    $(".imgIframe").off("click", img_iframe_handler).on("click", img_iframe_handler);
    $('.shareDeal').off("click", sharewish_handler).on('click', sharewish_handler);
    $('.share_store').off("click", share_store_handler).on("click", share_store_handler);
    $('.store_sharers').off("click", display_popup_handler).on("click", display_popup_handler);
    install_share_object_handler();
    install_delete_object_handler();
    $('a.wishimg-deal-homepage').fancybox({
        scrolling: 'yes',
        minWidth: 300,
        minHeight: 450,
        autoSize: true,
        scrolling: 'no',
        helpers : { overlay : { locked : false } }
    });
    $('.doLogin').on('click', login_handler);
    $('.suggestStore').on('click', suggest_store_handler);
    $('.contactUs').on('click', contact_us_handler);

});

