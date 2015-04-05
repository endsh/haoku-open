+ function ($) {
	'use strict';

	var $K = {
		success: function (message, selector, close) {
			this.show('success', message, selector, close)
		},

		error: function (message, selector, close) {
			this.show('danger', message, selector, close)
		},

		show: function (type, message, selector, close) {
			var html = '<div class="alert alert-' + type + '">'
			if (close !== false) {
				html += '<button class="close" type="button" data-dismiss="alert" aria-hidden="true">×</button>'
			}
			html += '<span>' + message + '</span></div>'

			if (typeof selector === 'undefined') {
				$('.message').html(html)
			} else {
				$(selector).html(html)
			}
		},

		hide: function (selector) {
			if (typeof selector === 'undefined') {
				$('.message').html('')
			} else {
				$(selector).html('')
			}
		}
	}

	window.$K = $K

}(jQuery)
