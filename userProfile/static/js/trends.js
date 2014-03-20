var get_trending_deals_handler = function(parent_category, sub_category)
{
    var $url = '/' + parent_category + '/'+ sub_category + '/trendingdeals/0/5/';
    var $element = $('#topDealsForStoreCategory');
    var $scrollContainer = $element.find(".scrollContainer");
    if ($scrollContainer && $scrollContainer.hasClass('mCustomScrollbar')) { 
      $scrollContainer.mCustomScrollbar("scrollTo","left");
    }
    $element.next().addClass("overlay");
    $.get($url, {}, function(data) {
          if(data.success === true) {
			var $data_container = $scrollContainer.find('.mCSB_container');
			if(!$data_container)
			    $data_container =  $scrollContainer

              $data_container.html(data.html);
              install_voting_handlers($scrollContainer);
              install_share_object_handler($element);

              $scrollContainer.attr("data-href", $url);
              $('a.wishimg-deal-homepage').fancybox({
                scrolling: 'yes',
                minWidth: 500,
                minHeight:450,
                autoSize: true,
                helpers : { overlay : { locked : false } }
              });
              $scrollContainer.mCustomScrollbar("update", true);
          } else {
              $scrollContainer.removeAttr("data-href");
          }
          $element.next().removeClass("overlay");
       });
    return false;
}

var get_top_stores_handler = function(parent_category, sub_category)
{
	var $element = $('#topStoresForStoreCategory');
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

    var $url = '/' + parent_category + '/'+ sub_category + '/trendingstores/v2/0/15/';
    $element.next().addClass("overlay");
    $.get($url, {}, function(data) {
    	if(data.success === true) {
            var $data_container = $scrollContainer.find('.mCSB_container');
            if(!$data_container)
                $data_container =  $scrollContainer

            $data_container.html(data.html);
            $data_container.find('.vendorFollowers').on("click", display_popup_handler);
            $scrollContainer.attr("data-href", $url);
            $scrollContainer.mCustomScrollbar("update", true);

            $('#trendingCategory').html(data.category);
            $('#trendingCategory').attr('href', data.search_url);

    	} else {
    		$scrollContainer.removeAttr("data-href");
    	}
        $element.next().removeClass("overlay");
    });
   	return false;
}

var get_top_reviews_handler = function(parent_category, sub_category)
{
    var $element = $('#topReviewsForStoreCategory');
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
    var $url = '/' + parent_category + '/'+ sub_category + '/trendingreviews/0/10/';
    $element.next().addClass("overlay");
    $.get($url, {}, function(data) {
    	if(data.success === true) {
            var $data_container = $scrollContainer.find('.mCSB_container');
            if(!$data_container)
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

var update_trends_handler = function(event, elementClicked)
{
  var $this = $(elementClicked);
  if ($this.hasClass('imageCategoryBoxSelected')) {
    // nothing to do
    return;
  } else {
    $('.updateTrends').removeClass('imageCategoryBoxSelected');
    $this.addClass('imageCategoryBoxSelected');
    var  parent_category_slug = $this.text().trim();
    var sub_category_slug = "all";
    get_top_reviews_handler(parent_category_slug, sub_category_slug);
    get_top_stores_handler(parent_category_slug, sub_category_slug);
    get_trending_deals_handler(parent_category_slug, sub_category_slug);
  }
	return false;
}

$(document).ready (function (){
    var _isCookieLoad = getCookie('_new_walkthrough');
    if (_isCookieLoad == undefined) {
        $('a#new-walk-through').fancybox({
                                            helpers : { overlay : { locked : false } }
                                        });

        $('a#new-walk-through').click();
        setCookie('_new_walkthrough', 0, 365);
    }
});