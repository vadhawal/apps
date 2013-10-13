var get_trending_deals_handler_auth = function(parent_category, sub_category)
{
    $.get('/' + parent_category + '/'+ sub_category + '/trendingdeals?v=1', {}, function(data) {
          $('#topDealsForStoreCategoryAuth').html(data);
            install_voting_handlers($('#topDealsForStoreCategoryAuth'));
            $('.shareWish').on('click', sharewish_handler);

            if($("#topDealsForStoreCategoryAuth").parent().hasClass('open-content'))
            {
	            $("#topDealsForStoreCategoryAuth").imagesLoaded({
	                complete: function(images) {
	                    $(".dealBox_v").mCustomScrollbar({
	                      verticalScroll:true,
	                      theme:"dark-thick",
	                      mouseWheel:true,
	                      autoHideScrollbar:true,
	                      contentTouchScroll:true
	                  	});
	                  	$(".mCSB_draggerContainer").css("margin-left", "10px");
	                }
	            });
	        }
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

var get_top_stores_handler_auth = function(parent_category, sub_category)
{
    $.get('/' + parent_category + '/'+ sub_category + '/trendingstores?v=1', {}, function(data) {
       $('#topStoresForStoreCategoryAuth').html(data);
       });
   	return false;
}

var get_top_reviews_handler_auth = function(parent_category, sub_category)
{
	$.get('/' + parent_category + '/'+ sub_category + '/trendingreviews?v=1', {}, function(data) {
       $('#topReviewsForStoreCategoryAuth').html(data);
       install_toggle_comment_handler();
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

