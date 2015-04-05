+ function ($) {
	'use strict';

	$(function () {
		function back2top() {
			setTimeout(function () {
				var scroll = $(window).scrollTop()
				if (scroll > 150) {
					$('.back2top').fadeIn(500)
				} else {
					$('.back2top').fadeOut(500)
				}
			}, 50)
		}

		back2top()

		$(window).scroll(back2top)

		$('.back2top').on('click', function () {
			$('body, html').animate({scrollTop: 0}, 1000)
		})
	})
} (jQuery)