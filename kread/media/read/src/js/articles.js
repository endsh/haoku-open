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