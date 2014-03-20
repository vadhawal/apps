var get_trending_deals_handler_auth = function(parent_category, sub_category)
{
	var $url = '/' + parent_category + '/'+ sub_category + '/trendingdeals/0/5/?v=1';
	var $element = $('#topDealsForStoreCategoryAuth');
    var $scrollContainer = $element.find(".scrollContainer");
	if ($scrollContainer && $scrollContainer.hasClass('mCustomScrollbar')) { 
		$scrollContainer.mCustomScrollbar("scrollTo","top");
	}
    $element.next().addClass("overlay");
    $.get($url, {}, function(data) {
    		if(data.success === true) {
                var $data_container = $scrollContainer.find('.mCSB_container');
                if(!$data_container || $data_container.length == 0)
                    $data_container =  $scrollContainer

	        	$data_container.html(data.html);
	            install_voting_handlers($element);
	            install_share_object_handler($element);

		        $scrollContainer.attr("data-href", $url);
	            $('a.wishimg-deal-homepage').fancybox({
	              scrolling: 'yes',
	              minWidth: 500,
	              minHeight:450,
	              autoSize: true,
	              helpers : { overlay : { locked : false } }
	            });
	        } else {
				$scrollContainer.removeAttr("data-href");
	        }
            $element.next().removeClass("overlay");
       });
    return false;
}

var get_top_stores_handler_auth = function(parent_category, sub_category)
{
    var $element = $('#topStoresForStoreCategoryAuth');
    if (!$element || $element.length == 0 ) {
        return;
    }
    var $scrollContainer = null;
    if ($element.hasClass("scrollContainer")) {
        $scrollContainer = $element;
    } else {
        $scrollContainer = $element.find(".scrollContainer");
    }
    if ($scrollContainer && $scrollContainer.hasClass('mCustomScrollbar')) { 
    	$scrollContainer.mCustomScrollbar("scrollTo","top");
    }
    var $url = '/' + parent_category + '/'+ sub_category + '/trendingstores/0/15/?v=1';
    $element.next().addClass("overlay");
    $.get($url, {}, function(data) {
    	if(data.success === true) {
            var $data_container = $scrollContainer.find('.mCSB_container');
            if(!$data_container || $data_container.length == 0)
                $data_container =  $scrollContainer

            $data_container.html(data.html);

            $scrollContainer.attr("data-href", $url);
            $data_container.find('.vendorFollowers').on("click", display_popup_handler);
    	} else {
    		$scrollContainer.removeAttr("data-href");
    	}
        $element.next().removeClass("overlay");
    });
   	return false;
}

var get_top_reviews_handler_auth = function(parent_category, sub_category)
{
    var $element = $('#topReviewsForStoreCategoryAuth');
    if (!$element || $element.length == 0 ) {
        return;
    }
    var $scrollContainer = null;
    if ($element.hasClass("scrollContainer")) {
        $scrollContainer = $element;
    } else {
        $scrollContainer = $element.find(".scrollContainer");
    }
    if ($scrollContainer && $scrollContainer.hasClass('mCustomScrollbar')) { 
    	$scrollContainer.mCustomScrollbar("scrollTo","top");
    }
    var $url = '/' + parent_category + '/'+ sub_category + '/trendingreviews/0/10/?v=1';
    $element.next().addClass("overlay");
    $.get($url, {}, function(data) {
    	if(data.success === true) {
            var $data_container = $scrollContainer.find('.mCSB_container');
            if(!$data_container || $data_container.length == 0)
                $data_container =  $scrollContainer

            $data_container.html(data.html);

		    $scrollContainer.attr("data-href", $url);
		    install_toggle_comment_handler();
        $data_container.find('.vendorFollowers').on("click", display_popup_handler);
    	} else {
    		$scrollContainer.removeAttr("data-href");
    	}
        $element.next().removeClass("overlay");
    });
	return false;
}

var update_trends_handler_auth = function(parent_category_slug)
{
    var sub_category_slug = "all";
    get_top_reviews_handler_auth(parent_category_slug, sub_category_slug);
    get_top_stores_handler_auth(parent_category_slug, sub_category_slug);
    get_trending_deals_handler_auth(parent_category_slug, sub_category_slug);
	return false;
}

$(document).ready(function(event){
	$('#dealsFilterSelect').change(function(){
		var slug = $(this).find("option:selected").text();
		update_trends_handler_auth(slug);
	});
});