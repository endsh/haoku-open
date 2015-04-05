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