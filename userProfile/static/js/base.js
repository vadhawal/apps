$(document).ready(function() {
    $('#getvendors').click(function(){
        var $blog_parentcategories = $(this).parent().parent().find('.blog_parentcategories');
        var subCategorySelect = $(this).parent().parent().find('.blog_subcategories');
        var parent_category_slug = $blog_parentcategories.find("option:selected").text();
        var sub_category_slug = subCategorySelect.find("option:selected").text();
        var disabled_sub_category_slug = subCategorySelect.find("option:disabled").text();

        if (sub_category_slug != disabled_sub_category_slug) {
            if(parent_category_slug && sub_category_slug)
                var url = "/getvendors/"+parent_category_slug+"/"+sub_category_slug+"/";
            else if(parent_category_slug && !sub_category_slug)
                var url = "/getvendors/"+parent_category_slug+"/all/";
            document.location.href = url;
        } else {
            subCategorySelect.addClass("error");
        }
    });

    $("#blog_parentcategories").val("empty");
    $("#blog_subcategories").val("empty");

    $('.blog_parentcategories').change(function(){
        var slug = $(this).find("option:selected").text();
        var $subCSelect = $(this).parent().find('.blog_subcategories');
        $subCSelect.removeClass("error");
        if(slug.toLowerCase() == "all") {
            $subCSelect.empty();
            var option = '<option value="all">All</option>';
            $subCSelect.append(option);
        } else {
            $.get('/' + slug + '/subcategories', {}, function(data) {
                $subCSelect.empty();
                var objJSON = eval("(function(){return " + data + ";})()");
                $subCSelect.append("<option value='empty' disabled selected>By Sub-category</option>");
                for(var i=0;i<objJSON.length;i++) {
                    var option = '<option value="'+objJSON[i]+'">'+objJSON[i]+'</option>';
                    $subCSelect.append(option);
                }
            });     
        }
    });
});