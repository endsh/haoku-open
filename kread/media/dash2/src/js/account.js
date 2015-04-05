+function ($) {
	'use strict';

	$(function () {

		var $body = $(document.body)

		if ($body.attr('id') == 'body-login') {
			$('#username_or_email').check()
			$('#password').check()
			$('#login-form').on('submit', function () {
				return $('#username_or_email, #password').check()
			})
		} else if ($body.attr('id') == 'body-register') {
			$('#username').check({
				min: 6, 
				max: 18,
				regx: {
					re: /^[\w\d]+[\d\w\_]+$/,
					message: '用户名只能包含英文字符，数字或下划线'
				},
				ajax: {
					url: '/account/check_username',
					key: 'username',
					message: '用户名已经被注册'
				}
			})
			$('#password').check({
				strip: false,
				min: 6, 
				max: 18,
				regx: {
					re: /^[\w\d\-\[\]{}|\\,.\/<>;:'"_`~!@#$%^&*()+= ]+$/,
					message: '密码只能包含英文字符，数字或其他可见字符'
				}
			})
			$('#repassword').check({
				strip: false,
				equal: {
					element: '#password',
					message: '两次密码不一致'
				}
			})
			$('#email').check({
				regx: {
					re: /^[\w\d]+[\d\w_.]+@([\d\w]+)\.([\d\w]+)(?:\.[\d\w]+)?$/
				},
				ajax: {
					url: '/account/check_email',
					key: 'email',
					message: '邮箱已经被注册'
				}
			})
			$('#register-form').on('submit', function () {
				return $('#username, #password, #repassword, #email').check()
			})
		}
	})

}(jQuery);