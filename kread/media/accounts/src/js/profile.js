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