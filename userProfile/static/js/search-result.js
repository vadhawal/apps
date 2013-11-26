var filterSearchHandler = function(event) {
	var $url = [location.protocol, '//', location.host, location.pathname].join('');
	$url = $url + '?filter=';
	$('.searchFilter :checked').each(function(i, selected){ 
  		$url += $(selected).val().toLowerCase() + '-'; 
	});
	$url = $url.slice(0,-1); //remove the extra last '-' seperator.
	window.location.href = $url;
}

function getParameters () {
	var prmstr = window.location.search.substr(1);
	var prmarr = prmstr.split ("&");
	var params = {};

	for ( var i = 0; i < prmarr.length; i++) {
		var tmparr = prmarr[i].split("=");
		params[tmparr[0]] = tmparr[1];
	}

	return params;
}

function updateCheckBoxes () {
	var params = getParameters();
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

$(document).ready(function(event){
	$('#searchResultFilter').on('click', filterSearchHandler);
	updateCheckBoxes();
});