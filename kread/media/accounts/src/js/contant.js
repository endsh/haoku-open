+ function ($) {
	'use strict'

	$(function () {
		var contant = {
			USERNAME_NULL: '用户名不能为空',
			USERNAME_TOO_SHORT: '用户名长度不能小于6个字符',
			USERNAME_TOO_LONG: '用户名长度不能超过18个字符',
			USERNAME_FORMAT_ERROR: '用户名只能包含英文字符，数字或下划线',
			USERNAME_EXISTS: '该用户名已被注册',
			PASSWORD_NULL: '密码不能为空',
			PASSWORD_TOO_SHORT: '密码长度不能大于6个字符',
			PASSWORD_TOO_LONG: '密码长度不能超过18个字符',
			PASSWORD_FORMAT_ERROR: '密码只能包含英文字符，数字或其他可见符号',
			REPASSWORD_DIFF: '两次密码不一致',
			EMAIL_TOO_LONG: '邮箱地址长度不能超过40个字符',
			EMAIL_FORMAT_ERROR: '邮箱地址格式不正确',
			EMAIL_EXISTS: '该邮箱地址已被注册',
			REGISTERING: '正在注册中...',
			REGISTER_SUCCESS: '注册成功',
			LOGINING: '正在登录中...',
			LOGIN_SUCCESS: '登录成功',
			LOGOUTING: '正在退出...',
			LOGOUT_SUCCESS: '退出成功',
			SUBMIT_SUCCESS: '提交成功',
			ACCESS_SUCCESS: '邮箱验证成功',
			RESET_SUCCESS: '密码已重置，请重新登录',
			SEND_SUCCESS: '邮件发送成功，请稍后查收'
		}

		window.contant = contant
	})

}(jQuery)
