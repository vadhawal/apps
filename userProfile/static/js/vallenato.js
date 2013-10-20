/*!
 * Vallenato 1.0
 * A Simple JQuery Accordion
 *
 * Designed by Switchroyale
 * 
 * Use Vallenato for whatever you want, enjoy!
 */

$(document).ready(function()
{
	//Add Inactive Class To All Accordion Headers
	$('.accordion-header').toggleClass('inactive-header');
	
	//Set The Accordion Content Width
	var contentwidth = $('.accordion-header').width();
	$('.accordion-content').css({'width' : contentwidth });
	
	//Open The First Accordion Section When Page Loads
	$('.accordion-header').first().toggleClass('active-header').toggleClass('inactive-header');
	$('.accordion-content').first().slideDown().toggleClass('open-content');

	var setupScrollBar = function ($contentElement) {
		/* If accordian is being opened and scrolling is not enabled alredy, enable it now. */

		if($contentElement.hasClass('open-content') && $contentElement.find('.mCustomScrollbar').length == 0)
		{
			$contentElement.imagesLoaded({
                complete: function(images) {
                    $contentElement.find(".scrollContainer").mCustomScrollbar({
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
	};
	
	// The Accordion Effect
	$('.accordion-header').click(function () {
		var $this = $(this);
		var $nextContentElement = null;

		if($this.is('.inactive-header')) {
			$('.active-header').toggleClass('active-header').toggleClass('inactive-header').next().slideToggle().toggleClass('open-content');
			$this.toggleClass('active-header').toggleClass('inactive-header');
			$nextContentElement = $this.next();
			$nextContentElement.slideToggle().toggleClass('open-content');
		}
		else {
			/* Disabling closure of already opened header */
			$this.toggleClass('active-header').toggleClass('inactive-header');
			$this.next().slideToggle().toggleClass('open-content');
			var $nextAccordianHeader = $this.next().next();
			if ($nextAccordianHeader.length) {
				$nextAccordianHeader.toggleClass('active-header').toggleClass('inactive-header');
				$nextContentElement = $nextAccordianHeader.next();
				$nextContentElement.slideToggle().toggleClass('open-content'); 
			} else {
				$('.accordion-header').first().toggleClass('active-header').toggleClass('inactive-header');
				$nextContentElement = $('.accordion-content').first();
				$nextContentElement.slideDown().toggleClass('open-content');
			}
		}
		setupScrollBar($nextContentElement);
	});
	
	return false;
});