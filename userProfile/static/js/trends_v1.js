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

    var $url = '/' + parent_category + '/'+ sub_category + '/trendingstores/0/15/';
    $element.next().addClass("overlay");
    $.get($url, {}, function(data) {
    	if(data.success === true) {
            var $data_container = $scrollContainer.find('.mCSB_container');
            if(!$data_container)
                $data_container =  $scrollContainer

            $data_container.html(data.html);
            $data_container.find('.vendorFollowers').on("click", display_popup_handler);
            $scrollContainer.attr("data-href", $url);
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

$(document).ready(function(event) {
    $('#walkthrough').pagewalkthrough({
        steps:
        [
               {
                   wrapper: '',
                   margin: 0,
                   popup:
                   {
                       content: '#type-modal',
                       type: 'modal',
                       offsetHorizontal: 0,
                       offsetVertical: 0,
                       width: '400'
                   }        
               },
               {
                   wrapper: '#loginWidget',
                   margin: '0',
                   popup:
                   {
                       content: '#type-tooltip-social-login',
                       type: 'tooltip',
                       position: 'bottom',
                       offsetHorizontal: 0,
                       offsetVertical: 0,
                       width: '500'
                   } ,
                   autoScroll: true    
               },
               {
                   wrapper: '#searchStoreBar',
                   margin: '0',
                   popup:
                   {
                       content: '#type-tooltip-search-store',
                       type: 'tooltip',
                       position: 'bottom',
                       offsetHorizontal: 0,
                       offsetVertical: 0,
                       width: '500',
                   } ,
                   autoScroll: true    
               },
               {
                   wrapper: '.categoryBox',
                   margin: '0',
                   popup:
                   {
                       content: '#type-tooltip-trend-category',
                       type: 'tooltip',
                       position: 'right',
                       offsetHorizontal: 0,
                       offsetVertical: 0,
                       width: '500',
                   } ,
                   autoScroll: true    
               },
               {
                   wrapper: '',
                   margin: '0',
                   popup:
                   {
                       content: '#done-walkthrough',
                       type: 'modal',
                       position: '',
                       offsetHorizontal: 0,
                       offsetVertical: 0,
                       width: '400'
                   }             
               },
        ],
        name: 'Walkthrough',
        onLoad: true,
        onClose: function(){
            $('.main-menu ul li a#open-walkthrough').removeClass('active');
            return true;
        },
        onCookieLoad: function(){
            return true;
        }

    });
        $('.main-menu ul li a').each(function(){
          $('.main-menu ul li').find('a.active').removeClass('active');
          $(this).live('click', function(){
              $(this).addClass('active');
              var id = $(this).attr('id').split('-');

              if(id == 'parameters') return;

              $.pagewalkthrough('show', id[1]); 
          });
      });


      $('.prev-step').live('click', function(e){
          $.pagewalkthrough('prev',e);
      });

      $('.next-step').live('click', function(e){
          $.pagewalkthrough('next',e);
      });

      $('.restart-step').live('click', function(e){
          $.pagewalkthrough('restart',e);
      });

      $('.close-step').live('click', function(e){
          $.pagewalkthrough('close');
      });
});
