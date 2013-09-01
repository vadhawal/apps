var get_trending_deals_handler = function(parent_category, sub_category)
{
    $.get('/' + parent_category + '/'+ sub_category + '/trendingdeals', {}, function(data) {
       $('#topDealsForStoreCategory').html(data);
            install_voting_handlers();
            $('.shareWish').on('click', sharewish_handler);
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
var update_trends_handler = function()
{
	var parent_category = $('#blog_parentcategories').find("option:selected").text();
	var sub_category = $('#blog_subcategories').find("option:selected").text();
	get_top_reviews_handler(parent_category, sub_category);
	get_top_stores_handler(parent_category, sub_category);
	get_trending_deals_handler(parent_category, sub_category);

	return false;
}