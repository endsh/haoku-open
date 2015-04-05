+ function ($) {
	'use strict'

	$(function () {
		var $body = $(document.body)
		var contant = window.contant
		var urls = window.urls

		if ($body.attr('id') === 'find-pass') {
			$('#email').check({
				max: 40,
				regx: {
					re: /^[\w\d]+[\d\w_.]+@([\d\w]+)\.([\d\w]+)(?:\.[\d\w]+)?$/
				}
			})
			$('#find-form').on('submit', function () {
				if ($('#email').check()) {
					$('#find-form').ajaxSubmit({
						success: function (data) {
							if (data.code === 0) {
								window.$K.success(contant.SEND_SUCCESS)
							} else {
								window.$K.error(data.msg)
								if (data.refresh === true) {
									var src = $('#verify_code_img').attr('data_src') + '&t=' + Math.random()
									$('#verify_code_img').attr('src', src)
								}
							}
						}
					})
				}
				return false
			})

		} else if ($body.attr('id') == 'reset-pass') {

			$('#password').check({
				strip: false,
				min: 6,
				max: 18,
				regx: {
					re: /^[\w\d\-\[\]{}|\\,.\/<>;:'"_`~!@#$%^&*()+= ]+$/,
					message: contant.PASSWORD_FORMAT_ERROR
				}
			})
			$('#repassword').check({
				strip: false,
				equal: {
					element: '#password',
					message: contant.REPASSWORD_DIFF
				}
			})
			$('#reset-form').on('submit', function () {
				if ($('#password, #repassword').check()) {
					$('#reset-form').ajaxSubmit({
						success: function (data) {
							if (data.code === 0) {
								window.$K.success(contant.RESET_SUCCESS)
								setTimeout(function () {
									window.location.href = urls.accounts.login
								}, 1000)
							} else {
								window.$K.error(data.msg)
							}
						}
					})
				}
				return false
			})
		}
	})
}(jQuery)