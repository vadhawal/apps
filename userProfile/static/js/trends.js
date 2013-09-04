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

  var parent_category_slug = $('#blog_parentcategories').find("option:selected").text();
  var subCategorySelect = $('#blog_subcategories');
  var sub_category_slug = subCategorySelect.find("option:selected").text();
  var disabled_sub_category_slug = subCategorySelect.find("option:disabled").text();

  if (sub_category_slug != disabled_sub_category_slug) {
    get_top_reviews_handler(parent_category_slug, sub_category_slug);
    get_top_stores_handler(parent_category_slug, sub_category_slug);
    get_trending_deals_handler(parent_category_slug, sub_category_slug);
  } else {
    subCategorySelect.addClass("error");
  }
  
	return false;
}