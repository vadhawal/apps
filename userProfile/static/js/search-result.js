var filterSearchHandler = function(event) {
	//var $url = [location.protocol, '//', location.host, location.pathname].join('');
	var params = getParameters();

	var $filterQuery = '';
	$('.searchFilter :checked').each(function(i, selected){ 
  		$filterQuery += $(selected).val().toLowerCase() + '-'; 
	});
	$filterQuery = $filterQuery.slice(0,-1); //remove the extra last '-' seperator.

    params.filter = $filterQuery;
	update_url(params, true);
}

function updateCheckBoxes () {
	var params = getParameters();
	if (params.hasOwnProperty("filter")) {
		var filters = params.filter.split('-');
		$('.searchFilter input[type="checkbox"]').each(function(i , checkbox){
			var $checkbox = $(checkbox);
			filters.forEach(function(filter){
				if ($checkbox.val() == filter) {
					$checkbox.prop("checked", true);
				}
			});
		});
	}
}

function updateSearchCategory () {
	var pathstr = window.location.pathname;
	var patharr = pathstr.split ("/");
	if (patharr[1].toLowerCase() == "stores") {
		var parentCategory = decodeURIComponent(patharr[2]);
		var subCategory = decodeURIComponent(patharr[3]);
		var parentSelect = $(".blog_parentcategories");
		var subSelect = $(".blog_subcategories");
		if (parentCategory.toLowerCase() == "all") {
			parentCategory = parentCategory.toLowerCase()
		}
		parentSelect.val(parentCategory);
		parentSelect.trigger("change");
		if (subCategory.toLowerCase() == "all") {
			subCategory = subCategory.toLowerCase()
		}
		subSelect.val(subCategory);
		subSelect.trigger("change");
	}
}

$(document).ready(function(event){
	$('#searchResultFilter').on('click', filterSearchHandler);
	updateCheckBoxes();
	updateSearchCategory();
});