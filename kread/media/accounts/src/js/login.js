+ function ($) {
	'use strict'

	$(function () {
		var $body = $(document.body)
		var contant = window.contant
		var urls = window.urls

		var sso = function () {
			$.getJSON(urls.accounts.sso, {}, function (data) {
				$.each(data.tokens, function (key, val) {
					$.ajax({
						type: 'GET',
						async: false,
						dataType: 'jsonp',
						jsonp: "jsonp",
						url: key,
						data: { token: val }
					})
				})
				setTimeout(function () {
					if (urls.jsonp !== '') {
						$.ajax({
							url: urls.jsonp,
							dataType: 'jsonp',
							jsonp: "jsonp"
						})
					} else {
						window.location.href = urls.next
					}
				}, 300)
			})
		}

		if ($body.attr('id') == 'login') {
			$('#account').check()
			$('#password').check()
			$('#login-form').on('submit', function () {
				if ($('#account, #password').check()) {
					window.$K.success(contant.LOGINING)
					$('#login-form').ajaxSubmit({
						success: function (data) {
							if (data.code === 0) {
								window.$K.success(contant.LOGIN_SUCCESS)
								sso()
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

			$('.btn-login').on('click', function () {
				sso()
			})
		}
	})
}(jQuery)