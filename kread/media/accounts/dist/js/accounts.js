/*
 * accounts - v1.0.0 - 2014-12-07
 * home: http://accounts.haoku.net/
 * Copyright (c) 2014 HaoKu Inc. All Rights Reserved.
 */

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

+ function ($) {
	'use strict'

	var Check = function (element, options) {
		var check = $.proxy(this.check, this)
		var error = $.proxy(this.error, this)
		this.$element = $(element)
		this.$form = this.$element.parents('form')
		this.label = typeof options.label !== 'undefined' ? options.label : this.$element.attr('data_label')
		this.options = $.extend({}, Check.DEFAULTS, options)
		if (typeof options.ajax === 'undefined') {
			this.$element.on('change', check)
		} else {
			var that = this
			this.$element.on('change', function () {
				if (check() !== false) {
					var args = {}
					args[options.ajax.key] = that.$element.val()
					$.get(options.ajax.url, args, function (data) {
						if (data.code !== 0) {
							error(data.msg)
						} else {
							window.$K.hide()
						}
					}, 'json')
				}
			})
		}
	}

	Check.DEFAULTS = {
		strip: true,
		empty: true
	}

	Check.prototype.check = function () {
		if (this.options.strip) {
			this.$element.val($.trim(this.$element.val()))
		}
		var val = this.$element.val()
		if (this.options.empty) {
			if (val.length === 0) {
				return this.error(this.label + '不能为空')
			}
		}
		if (typeof this.options.min !== 'undefined') {
			if (val.length < this.options.min) {
				return this.error(this.label + '长度不能小于' + this.options.min + '个字符')
			}
		}
		if (typeof this.options.max !== 'undefined') {
			if (val.length > this.options.max) {
				return this.error(this.label + '长度不能大于' + this.options.max + '个字符')
			}
		}
		if (typeof this.options.equal == 'object') {
			if (val != $(this.options.equal.element).val()) {
				return this.error(this.options.equal.message)
			}
		}
		if (typeof this.options.regx == 'object') {
			if (!val.match(this.options.regx.re)) {
				if (this.options.regx.message) {
					return this.error(this.options.regx.message)
				} else {
					return this.error(this.label + '格式不正确')
				}
			}
		}
	}

	Check.prototype.error = function (message) {
		if (typeof this.options.error !== 'undefined') {
			if (typeof this.options.error === 'string') {
				window.$K.error(message, this.options.error)
			} else {
				this.options.error(message)
			}			
		} else {
			window.$K.error(message)
		}
		return false
	}

	function Plugin(option) {
		var res = true
		this.each(function () {
			var $this = $(this)
			var data = $this.data('hk.check')
			var options = $.extend({}, Check.DEFAULTS, typeof option == 'object' && option)

			if (!data) {
				$this.data('hk.check', (data = new Check(this, options)))
			} else {
				if (data.check() === false) {
					res = false
					return false
				}
			}
		})
		return res
	}

	var old = $.fn.check

	$.fn.check = Plugin
	$.fn.check.Constructor = Check

	$.fn.check.noConflict = function () {
		$.fn.check = old
		return this
	}

}(jQuery)

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
+ function ($) {
	'use strict'

	$(function () {

		var $window = $(window)
		var $body = $(document.body)
		var $K = window.$K
		var contant = window.contant
		var urls = window.urls

		if ($body.attr('id') === 'profile') {

			$body.scrollspy({
				target: '.sidebar'
			})

			$window.on('load', function () {
				$body.scrollspy('refresh')
			})

			setTimeout(function () {
				var $sidebar = $('.sidebar')
				$sidebar.affix({
					offset: {
						top: function () {
							var offsetTop = $sidebar.offset().top
							var sidebarMargin = parseInt($sidebar.children(0).css('margin-top'), 10)
							var navbarHeight = $('.navbar').height()
							return (this.top = offsetTop - navbarHeight - sidebarMargin)
						},
						bottom: function () {
							return (this.bottom = $('.footer').outerHeight(true))
						}
					}
				})
				$window.trigger('scroll')
			})

			$('#avatar').on('change', function () {
				$('#avatar-form').ajaxSubmit({
					success: function (data) {
						if (data.code === 0) {
							$('.avatar').attr('src', data.avatar + '?t=' + Math.random())
						}
						return false
					}
				})
				return false
			})

			var $profileForm = $('#profile-form')
			$profileForm.on('submit', function () {
				$profileForm.ajaxSubmit({
					success: function (data) {
						if (data.code === 0) {
							$K.success(contant.SUBMIT_SUCCESS, '.profile-message')
						} else {
							$K.error(data.msg, '.profile-message')
						}
					}
				})
				return false
			})

			var $changeForm = $('#change-form')
			$('#oldpassword').check({
				strip: false,
				error: '.change-message'
			})
			$('#password').check({
				strip: false,
				min: 6,
				max: 18,
				regx: {
					re: /^[\w\d\-\[\]{}|\\,.\/<>;:'"_`~!@#$%^&*()+= ]+$/,
					message: contant.PASSWORD_FORMAT_ERROR
				},
				error: '.change-message'
			})
			$('#repassword').check({
				strip: false,
				equal: {
					element: '#password',
					message: contant.REPASSWORD_DIFF
				},
				error: '.change-message'
			})
			$changeForm.on('submit', function () {
				if ($('#oldpassword, #password, #repassword').check()) {
					$changeForm.ajaxSubmit({
						success: function (data) {
							if (data.code === 0) {
								$K.success(contant.SUBMIT_SUCCESS, '.change-message')
								setTimeout(function () {
									window.location.href = urls.accounts.logout
								}, 300)
							} else {
								$K.error(data.msg, '.change-message')
							}
						}
					})
				}
				return false
			})

			$('#btn-email').on('click', function () {
				var $this = $(this)
				$this.button('loading')
				$.ajax({
					url: urls.profile.bind_email,
					type: 'POST',
					success: function (data) {
						if (data.code === 0) {
							if (data.access === 1) {
								$K.success(contant.ACCESS_SUCCESS, '.bind-message')
								$this.html('验证通过')
							} else {
								$K.success(contant.SEND_SUCCESS, '.bind-message')
								$this.html('等待验证')
							}
						} else {
							$K.error(data.msg, '.bind-message')
						}
					}
				})
			})
		}
	});
}(jQuery);
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