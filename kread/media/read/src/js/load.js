+ function ($) {
	'use strict';

	$(function () {
		$('.load-more').on('click', function () {
			var $this = $(this)
			var url = $this.data('url')
			var target = $this.data('target')
			var $target = $(target)

			if (url !== '' && typeof url !== 'undefined') {
				$this.button('loading')
				$.getJSON(url, {}, function (data) {
					if (data.code === 0) {
						$target.append(data.html)
						if (data.url === '' || typeof data.url === 'undefined') {
							$this.data('url', '')
							$this.html('没有了')
							$this.addClass('disabled')
						} else {
							$this.data('url', data.url)
							$this.button('reset')
						}
					} else {
						$this.html('没有了')
						$this.addClass('disabled')
					}
				})
			}
		})
	})
} (jQuery)