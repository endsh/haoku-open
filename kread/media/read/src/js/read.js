+ function ($) {
	'use strict';

	$(function () {
		var $window = $(window)
		setTimeout(function () {
			var $hots = $('.section-hots')
			$hots.affix({
				offset: {
					top: function () {
						var offsetTop = $hots.offset().top
						var margin = parseInt($hots.children(0).css('margin-top'), 10)
						var navbarHeight = $('.navbar').height()
						return (this.top = offsetTop - navbarHeight - margin)
					},
					bottom: function () {
						var marginBottom = parseInt($hots.css('margin-bottom'), 0) - 28
						return (this.bottom = $('.footer').outerHeight(true) + marginBottom)
					}
				}
			})
			$window.trigger('scroll')
		})
	})
}(jQuery)