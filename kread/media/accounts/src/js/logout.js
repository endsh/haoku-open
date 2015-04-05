+ function ($) {
	'use strict'

	$(function () {
		var $body = $(document.body)
		var contant = window.contant
		var urls = window.urls

		if ($body.attr('id') == 'logout') {
			window.$K.success(contant.LOGOUTING)
			$.each(window.hosts, function (_, url) {
				$.ajax({
					type: 'GET',
					async: false,
					dataType: 'jsonp',
					url: url
				})
			})
			window.$K.success(contant.LOGOUT_SUCCESS)
			setTimeout(function () {
				window.location.href = urls.next
			}, 1000)
		}
	})
}(jQuery)