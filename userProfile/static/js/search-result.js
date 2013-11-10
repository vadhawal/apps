var filterSearchHandler = function(event) {
	var $url = [location.protocol, '//', location.host, location.pathname].join('');
	$url = $url + '?filter=';
	$('#filtersSelect :selected').each(function(i, selected){ 
  		$url += $(selected).val().toLowerCase() + '-'; 
	});
	$url = $url.slice(0,-1); //remove the extra last '-' seperator.
	window.location.href = $url;
}

$(document).ready(function(event){
	$('#searchResultFilter').on('click', filterSearchHandler);
});