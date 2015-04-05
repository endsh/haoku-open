+ function ($) {
	'use strict'

	$(function () {
		var $body = $(document.body)
		var contant = window.contant
		var urls = window.urls

		if ($body.attr('id') == 'register') {
			$('#username').check({
				min: 6,
				max: 18,
				regx: {
					re: /^[\w\d]+[\d\w\_]+$/,
					message: contant.USERNAME_FORMAT_ERROR
				},
				ajax: {
					url: urls.accounts.check,
					key: 'username',
					message: contant.USERNAME_EXISTS
				}
			})
			$('#password').check({
				strip: false,
				min: 6,
				max: 18,
				regx: {
					re: /^[\w\d\-\[\]{}|\\,.\/<>;:'"_`~!@#$%^&*()+= ]+$/,
					message: contant.PASSWORD_FORMAT_ERROR
				}
			})
			$('#email').check({
				max: 40,
				regx: {
					re: /^[\w\d]+[\d\w_.]+@([\d\w]+)\.([\d\w]+)(?:\.[\d\w]+)?$/
				},
				ajax: {
					url: urls.accounts.check,
					key: 'email',
					message: contant.EMAIL_EXISTS
				}
			})

			$('#register-form').on('submit', function () {
				if ($('#username, #password, #email').check()) {
					window.$K.success(contant.REGISTERING)
					$('#register-form').ajaxSubmit({
						success: function (data) {
							if (data.code === 0) {
								window.$K.success(contant.REGISTER_SUCCESS)
								setTimeout(function () {
									window.location.href = urls.accounts.login
								}, 1000)
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
		}
	})
}(jQuery)