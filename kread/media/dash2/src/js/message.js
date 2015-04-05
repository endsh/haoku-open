+function ($) {
	'use strict';

	var $K = {
		success: function (message, close) {
			this.show('success', message, close)
		},

		error: function (message, close) {
			this.show('danger', message, close)
		},

		show: function (type, message, close) {
			var html = '<div class="alert alert-' + type + '">'
			if (close !== false) {
				html += '<button class="close" type="button" data-dismiss="alert" aria-hidden="true">×</button>'
			}
			html += '<span>' + message + '</span></div>'
			$('.k-message').html(html)
		},

		hide: function () {
			$('.k-message').html('')
		}
	}

	window.$K = $K

}(jQuery);
