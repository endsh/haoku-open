/*
 * read - v1.0.0 - 2014-12-18
 * home: http://www.haoku.net/
 * Copyright (c) 2014 HaoKu Inc. All Rights Reserved.
 */
+ function ($) {
	'use strict';

	$(function () {
		var $window = $(window)
		setTimeout(function () {
			var $hots = $('.section-hots')
			$hots.affix({
				offset: {
					top: function () {
						var offsetTop = $hots.offset().top
						var margin = parseInt($hots.children(0).css('margin-top'), 10)
						var navbarHeight = $('.navbar').height()
						return (this.top = offsetTop - navbarHeight - margin)
					},
					bottom: function () {
						var marginBottom = parseInt($hots.css('margin-bottom'), 0) - 28
						return (this.bottom = $('.footer').outerHeight(true) + marginBottom)
					}
				}
			})
			$window.trigger('scroll')
		})
	})
}(jQuery)
+ function ($) {
	'use strict';

	$(function () {
		$('.load-more').on('click', function () {
			var $this = $(this)
			var url = $this.data('url')
			var target = $this.data('target')
			var $target = $(target)

			if (url !== '' && typeof url !== 'undefined') {
				$this.button('loading')
				$.getJSON(url, {}, function (data) {
					if (data.code === 0) {
						$target.append(data.html)
						if (data.url === '' || typeof data.url === 'undefined') {
							$this.data('url', '')
							$this.html('没有了')
							$this.addClass('disabled')
						} else {
							$this.data('url', data.url)
							$this.button('reset')
						}
					} else {
						$this.html('没有了')
						$this.addClass('disabled')
					}
				})
			}
		})
	})
} (jQuery)
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
	$('#topic-more').click(function () {
		var last = $('#topic-more').attr('data-last');
		var word = $('#topic-more').attr('data-word');
		var target = $($('#topic-more').attr('data-target'));
		$.get('/topics', {word:word, last:last}, function (data) {
			if (data.code == 0) {
				target.append(data.html);
			}
		});
	});
} (jQuery);
+ function ($) {
	'use strict';

	$(function () {
		var $K = window.$K
		var $textarea = $(".comments textarea")
		$textarea.focus(function () {
			$textarea.animate({height:'100px'}, 300)
		})
		$textarea.blur(function () {
			if ($textarea.val() === '') {
				$textarea.animate({height:'60px'}, 300)				
			}
		})

		function _escape(text) {
			return $('.text-holder').text(text).html()
		}

		$('#comment-form').on('submit', function () {
			$(this).ajaxSubmit({
				success: function (data) {
					if (data.code == 0) {
						var comment = data.comment
						var html = ['<li><img class="avatar avatar-normal" src="']
						html.push(_escape(comment.avatar))
						html.push('"><div class="comment-user"><span class="name">')
						html.push(_escape(comment.nickname))
						html.push('</span><span class="data">')
						html.push(_escape(comment.pubdate))
						html.push('</span><span class="num pull-right">#')
						html.push(_escape(comment.num))
						html.push('楼</span></div><p class="comment-content">')
						html.push(_escape(comment.content))
						html.push('</p></li>')
						html = html.join('')
						$('.comments-box').prepend(html)
					} else {
						$K.error(data.msg)
					}
				}
			})
			return false;
		})
	})
}(jQuery);

+ function ($) {
    'use strict';

    $(function () {

        var share = window.article
        $('.share').on('click', function () {
            var to = $(this).data('to'), url = '', args = [
                'url=' + encodeURIComponent(share.url)
            ]
            if (to === 'qq')
                url = 'http://connect.qq.com/widget/shareqq/index.html?',
                args.push('&desc=' + share.title),
                args.push('&site=' + encodeURIComponent('好酷网'))
            else if (to === 'weibo')
                url = 'http://v.t.sina.com.cn/share/share.php?',
                args.push('&appkey=2499394483'),
                args.push('&title=' + share.title),
                args.push('&pic=' + share.image),
                args.push('&ralateUid=2493118952')
            else if (to === 'tencent')
                url = 'http://share.v.t.qq.com/index.php?c=share&a=index&',
                args.push('&appkey=801088644'),
                args.push('&title=' + share.title),
                args.push('&pic=' + share.image),
                args.push('&assname=imhaoku')
            else if (to === 'qzone')
                url = 'http://sns.qzone.qq.com/cgi-bin/qzshare/cgi_qzshare_onekey?',
                args.push('&title=' + share.title),
                args.push('&pics=' + share.image)
            else
                return
            args = args.join('')
            window.open(url + args)
        })
    })
}(jQuery)
+ function ($) {
	'use strict';

	$(function () {
		function back2top() {
			setTimeout(function () {
				var scroll = $(window).scrollTop()
				if (scroll > 150) {
					$('.back2top').fadeIn(500)
				} else {
					$('.back2top').fadeOut(500)
				}
			}, 50)
		}

		back2top()

		$(window).scroll(back2top)

		$('.back2top').on('click', function () {
			$('body, html').animate({scrollTop: 0}, 1000)
		})
	})
} (jQuery)