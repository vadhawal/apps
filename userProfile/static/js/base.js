var setupCustomScrollBar = function ($element, horizontal_scroll) {
    if (!$element || $element.length == 0 ) {
        return;
    }
    var $scrollContainer = null;
    if ($element.hasClass("scrollContainer")) {
        $scrollContainer = $element;
    } else {
        $scrollContainer = $element.find(".scrollContainer");
    }
    var totalScrollCallback = function(){
        var $href = $scrollContainer.attr("data-href");
        if($href) {
            var a = $('<a>', { href:$href } )[0];
            var $pathname = a.pathname;
            var pathsplit = $pathname.split("/");
            var lIndex = pathsplit[pathsplit.length-2];
            var sIndex = pathsplit[pathsplit.length-3];
            var $chunk = $scrollContainer.data("chunk");
            pathsplit[pathsplit.length-2] = parseInt(lIndex) + parseInt($chunk);
            pathsplit[pathsplit.length-3] = parseInt(lIndex);
            $pathname = pathsplit.join('/');
            var $url = $pathname + a.search; //a,search contains any GET query parameter.
            $.get($url, {}, function(data) {
                if(data.success === true) {
                    $scrollContainer.find('.mCSB_container').append(data.html);
                    install_voting_handlers($scrollContainer);
                    install_share_object_handler($scrollContainer);
                    $scrollContainer.find('.vendorFollowers').on("click", display_popup_handler);
                    $scrollContainer.attr("data-href", $url);

                    $scrollContainer.find($('a.wishimg-deal-homepage')).fancybox({
                      scrolling: 'yes',
                      minWidth: 500,
                      minHeight:450,
                      autoSize: true,
                      helpers : { overlay : { locked : false } }
                    });

                    if (horizontal_scroll) {
                        // this needs to be done for horizontal scrollbar as the size doesnt seem to get update manually
                        var horizontalUpdateTimer = setTimeout(function(){
                            $scrollContainer.mCustomScrollbar("update", true);
                        }, 500);
                    }
                } else {
                    $scrollContainer.removeAttr("data-href");
                }
            });
        }
    };

    if ($scrollContainer && !$scrollContainer.hasClass('mCustomScrollbar')) {
        $scrollContainer.imagesLoaded({
            complete: function(images) {
                if(horizontal_scroll) {
                    $scrollContainer.mCustomScrollbar({
                        horizontalScroll:true,
                        theme:"dark-thick",
                        mouseWheel:true,
                        autoHideScrollbar:true,
                        contentTouchScroll:true,
                        autoDraggerLength: true,
                        callbacks: {
                            onTotalScroll: totalScrollCallback//, // Will be called once scroll reaches bottom.
                            //onTotalScrollOffset:100 //onTotalScroll callback will be fired 100 pixels before bottom.
                        },
                        advanced:{
                            //autoExpandHorizontalScroll: true, // Dont switch on this flag!! This causes a flicker with css:hover as elements are wrapped unwrapped
                            updateOnContentResize: true //Will update the scrollbar size automatically once the data is loaded.
                        }
                    });
                } else {
                    $scrollContainer.mCustomScrollbar({
                        verticalScroll:true,
                        theme:"dark-thick",
                        mouseWheel:true,
                        autoHideScrollbar:true,
                        contentTouchScroll:true,
                        callbacks: {
                            onTotalScroll: totalScrollCallback,
                            onTotalScrollOffset:100
                        },
                        advanced:{
                            updateOnContentResize: true
                        }
                    });                    
                }
                $(".mCSB_draggerContainer").css("margin-left", "10px");
            }
        });
    } else if ($scrollContainer) {
        $scrollContainer.mCustomScrollbar("update");
    }
};

$(window).load(function(){
    setupCustomScrollBar($(".accordion-content").first());
});

var build_category_menu_handler = function() {
	var ul = $("<ul/>")
        .attr("role", "menu")
        .addClass("dropdown-menu dropdown-menu-parent");

    $.each(category_namespace.categories, function(object) {
    	var category_li = $("<li/>").addClass("dropdown-submenu");
	    var category_a = $("<a/>")
	        	.html(object)
	            .appendTo(category_li)
	            .addClass('dropdown-parent-category')
	    var sub_category_ul = $("<ul/>")
        					.addClass("dropdown-menu");

        category_li.append(sub_category_ul);

        for(var i=0;i<this.length;i++) {
	        var li = $("<li/>")
	            .appendTo(sub_category_ul);

	        var a = $("<a/>")
	        	.html(this[i])
	            .appendTo(li)
	            .on('click', function(event){
			        var parent_category_slug = $(this).parents('.dropdown-submenu').find('.dropdown-parent-category').text();
			        var sub_category_slug = $(this).text();

			        if(parent_category_slug && sub_category_slug) {
			            var url = "/stores/"+parent_category_slug+"/"+sub_category_slug+"/";
			            document.location.href = url;
			        }
			        return false;
	            });
        }
        ul.append(category_li);

    });
    $('.searchCategory').append(ul);
}

$(document).ready(function() {
    $('#getvendors').click(function(){
        var $blog_parentcategories = $(this).parent().parent().parent().find('.blog_parentcategories');
        var $subCategorySelect = $(this).parent().parent().parent().find('.blog_subcategories');
        var parent_category_slug = $blog_parentcategories.find("option:selected").text();
        var sub_category_slug = $subCategorySelect.find("option:selected").text();
        var disabled_sub_category_slug = $subCategorySelect.find("option:disabled").text();
        var disabled_parent_category_slug = $blog_parentcategories.find("option:disabled").text();

        if (sub_category_slug != disabled_sub_category_slug && disabled_parent_category_slug != parent_category_slug) {
            if(parent_category_slug && sub_category_slug)
                var url = "/stores/"+parent_category_slug+"/"+sub_category_slug+"/";
            else if(parent_category_slug && !sub_category_slug)
                var url = "/stores/"+parent_category_slug+"/all/";
            document.location.href = url;
        } 
        if ( sub_category_slug == disabled_sub_category_slug ) {
            $subCategorySelect.addClass("error");
        }
        if ( parent_category_slug == disabled_parent_category_slug ) {
            $blog_parentcategories.addClass("error");
        }
    });

    $(".blog_parentcategories").val("empty");
    $(".blog_subcategories").val("empty");


    $('.blog_subcategories').change(function(){
        $(this).removeClass("error");
    });

    $('.blog_parentcategories').change(function(){
        var $this = $(this);
        var slug = $this.find("option:selected").text();
        var $subCSelect = $this.parent().parent().find('.blog_subcategories');
        $this.removeClass("error");
        if(slug.toLowerCase() == "all") {
            $subCSelect.empty();
            $subCSelect.removeClass("error");
            var option = '<option value="all">All</option>';
            $subCSelect.append(option);
        } else {
            $subCSelect.empty();
            var data = category_namespace.categories;
            // slug = slug.toLowerCase();
            var objJSON = data[slug];
            $subCSelect.append("<option value='empty' disabled selected>By Sub-category</option>");
            for(var i=0;i<objJSON.length;i++) {
                    var option = '<option value="'+objJSON[i]+'">'+objJSON[i]+'</option>';
                    $subCSelect.append(option);
            }
            /* code to fetch categories from AJAX GET requests. Disabled for now.
             * Category list is preloaded as JSON.
             */
            /* $.get('/' + slug + '/subcategories', {}, function(data) {
                $subCSelect.empty();
                var objJSON = eval("(function(){return " + data + ";})()");
                $subCSelect.append("<option value='empty' disabled selected>By Sub-category</option>");
                for(var i=0;i<objJSON.length;i++) {
                    var option = '<option value="'+objJSON[i]+'">'+objJSON[i]+'</option>';
                    $subCSelect.append(option);
                }
            }); */    
        }
    });
	build_category_menu_handler();
	$('.dropdown-toggle').on('click', function(){
		$('.dropdown-menu-parent').toggle();//css({'display':'block'});
		return false;
	});
});