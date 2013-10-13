$(document).ready(function() {
    $('#getvendors').click(function(){
        var $blog_parentcategories = $(this).parent().parent().parent().find('.blog_parentcategories');
        var $subCategorySelect = $(this).parent().parent().parent().find('.blog_subcategories');
        var parent_category_slug = $blog_parentcategories.find("option:selected").text();
        var sub_category_slug = $subCategorySelect.find("option:selected").text();
        var disabled_sub_category_slug = $subCategorySelect.find("option:disabled").text();
        var disabled_parent_category_slug = $blog_parentcategories.find("option:disabled").text();

        if (sub_category_slug != disabled_sub_category_slug && disabled_parent_category_slug != parent_category_slug) {
            if(parent_category_slug && sub_category_slug)
                var url = "/getvendors/"+parent_category_slug+"/"+sub_category_slug+"/";
            else if(parent_category_slug && !sub_category_slug)
                var url = "/getvendors/"+parent_category_slug+"/all/";
            document.location.href = url;
        } 
        if ( sub_category_slug == disabled_sub_category_slug ) {
            $subCategorySelect.addClass("error");
        }
        if ( parent_category_slug == disabled_parent_category_slug ) {
            $blog_parentcategories.addClass("error");
        }
    });

    $(".settings").click(function(){
        var $settingsPopup = $('.settingsPopup');
        if ($settingsPopup.hasClass('hide')) {
            $settingsPopup.removeClass('hide');
            $settingsPopup.css({'top': $(this).height(), 'left': -90});
        } else {
            $settingsPopup.addClass('hide');
        }
    });

    $(".blog_parentcategories").val("empty");
    $(".blog_subcategories").val("empty");

    $('.blog_parentcategories').change(function(){
        var $this = $(this);
        var slug = $this.find("option:selected").text();
        var $subCSelect = $this.parent().parent().find('.blog_subcategories');
        $subCSelect.removeClass("error");
        $this.removeClass("error");
        if(slug.toLowerCase() == "all") {
            $subCSelect.empty();
            var option = '<option value="all">All</option>';
            $subCSelect.append(option);
        } else {
            $subCSelect.empty();
            var data = category_namespace.categories;
            slug = slug.toLowerCase();
            var objJSON = data[slug];
            $subCSelect.append("<option value='empty' disabled selected>By Sub-category</option>");
            for(var i=0;i<objJSON.length;i++) {
                    var option = '<option value="'+objJSON[i]+'">'+objJSON[i]+'</option>';
                    $subCSelect.append(option);
            }
            /* code to fetch categories from AJAX GET requests. Disabled for now.
             * Category list is preloaded as JSON.
             */
            /* $.get('/' + slug + '/subcategories', {}, function(data) {
                $subCSelect.empty();
                var objJSON = eval("(function(){return " + data + ";})()");
                $subCSelect.append("<option value='empty' disabled selected>By Sub-category</option>");
                for(var i=0;i<objJSON.length;i++) {
                    var option = '<option value="'+objJSON[i]+'">'+objJSON[i]+'</option>';
                    $subCSelect.append(option);
                }
            }); */    
        }
    });
});