/*!
 * Documenter 2.0
 * http://rxa.li/documenter
 *
 * Copyright 2013, Xaver Birsak
 * http://revaxarts.com
 *
 */
 

!function ($) {
  $(function(){
	  
/*=============================================
	=         scrolling nav Active          =
=============================================*/
var scrollLink = $('.page-scroll');
// Active link switching
$(window).scroll(function () {
	var scrollbarLocation = $(this).scrollTop();

	scrollLink.each(function () {

		var sectionOffset = $(this.hash).offset().top - 90;

		if (sectionOffset <= scrollbarLocation) {
			$(this).parent().addClass('active');
			$(this).parent().siblings().removeClass('active');
		}
	});
});	 

	
})
}(window.jQuery)