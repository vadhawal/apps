var get_trending_deals_handler = function(parent_category, sub_category)
{
    $.get('/' + parent_category + '/'+ sub_category + '/trendingdeals', {}, function(data) {
          $('#topDealsForStoreCategory').html(data);
            install_voting_handlers();
            $('.shareWish').on('click', sharewish_handler);

            $("#topDealsForStoreCategory").imagesLoaded({
                complete: function(images) {
                    $(".dealBox_h").mCustomScrollbar({
                      horizontalScroll:true,
                      theme:"dark-thick",
                      mouseWheel:true,
                      autoHideScrollbar:true,
                      contentTouchScroll:true
                  });
                }
            });

            $('a.wishimg-deal-homepage').fancybox({
              scrolling: 'yes',
              minWidth: 500,
              minHeight:450,
              autoSize: true,
              helpers : { overlay : { locked : false } }
            });
       });
    return false;
}

var get_top_stores_handler = function(parent_category, sub_category)
{
    $.get('/' + parent_category + '/'+ sub_category + '/trendingstores', {}, function(data) {
       $('#topStoresForStoreCategory').html(data);
       });
   	return false;
}

var get_top_reviews_handler = function(parent_category, sub_category)
{
	$.get('/' + parent_category + '/'+ sub_category + '/trendingreviews', {}, function(data) {
       $('#topReviewsForStoreCategory').html(data);
       install_toggle_comment_handler();
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

