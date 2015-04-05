$(function () {
	var container = $('#placeholder');

	var labels = {
		fetch: '下载统计',
		fetch_cate: '下载分类',
		fetch_art: '下载文章',
		fetch_img: '下载图片',
		fetch_page: '下载分页',
		article: '文章处理',
		article_ext: '提取正文',
		article_url: '文章链接',
		article_pag: '文章分页',
		article_mer: '分页合并',
		article_img: '文章图片',
		article_mea: '图片处理',
		article_sim: '相似过滤',
		article_seg: '分词处理'
	};

	var exts = {
		domain_wait: '分类等待',
		domain_doing: '分类处理',
		article_wait: '文章等待',
		article_load: '文章加载',
	};

	function inArray(obj, arr) {
		for (var i = 0; i < arr.length; ++i) {
			if (arr[i] == obj) {
				return true;
			}
		}
		return false;
	}

	var keys = ['fetch', 'fetch_err'];
	var datas = new Object();

	var choiceContainer = $("#choices");
	$.each(labels, function(key, val) {
		var html = '<label>' + val + ': </label> ';
		html += '<input type="checkbox" id="' + key + '" name="' + key + '"';
		if (inArray(key, keys)) {
			html += ' checked';
		}
		html += '><label for="' + key + '">完成</label>';

		var errKey = key + '_err';
		html += ' - <input type="checkbox" id="' + errKey + '" name="' + errKey + '"';
		if (inArray(errKey, keys)) {
			html += ' checked';
		}
		html += '><label for="' + errKey + '">错误</label>';

		html = '<div>' + html + '</div>';
		choiceContainer.append(html);


		datas[key] = {label:val, data:[]};
		for (var i = 0; i < 60; i += 1) {
			datas[key].data.push([i, 0]);
		}

		datas[errKey] = {label:val + ' - ' + '错误', data:[]};
		for (var i = 0; i < 60; i += 1) {
			datas[errKey].data.push([i, 0]);
		}
	});
	console.log(datas);

	choiceContainer.find("input").click(function () {
		keys = [];
		choiceContainer.find("input:checked").each(function () {
			var key = $(this).attr("name");
			keys.push(key);
		});
	});

	function draw() {
		data = [];
		for (var i = 0; i < keys.length; i += 1) {
			data.push(datas[keys[i]]);
		}

		$.plot(container, data, {
			yaxis: {
				min: 0
			},
			xaxis: {
				tickDecimals: 0
			}
		});
	}

	function KMG(number) {
		if (number != undefined) {
			if (number < 1024) {
				return number + 'KB';
			}
			return (number / 1024).toFixed(2) + 'MB';
		}
		return '0KB';
	}

	function updateCounts(count, number, doing, other) {
		var html = '';
		$.each(labels, function (key, val) {
			html += '<div class="col-md-3" style="margin-bottom: 4px;font-size:16px;"><div>';
			html += '<span class="label label-default">' + val + '</span> ';
			html += '<span class="label label-success">' + (count[key] || 0) + '</span> ';
			html += '<span class="label label-danger">' + (count[key + '_err'] || 0) + '</span> ';
			html += '<span class="label label-info">' + (doing[key] || 0) + '</span> ' 
			html += '</div></div>';
		});

		$.each(exts, function (key, val) {
			html += '<div class="col-md-3" style="margin-bottom: 4px;font-size:16px;"><div>';
			html += '<span class="label label-default">' + val + '</span> ';
			html += '<span class="label label-info">' + (doing[key] || 0) + '</span> ' 
			html += '</div></div>';
		});

		html += '<div class="col-md-3" style="margin-bottom: 4px;font-size:16px;"><div>';
		html += '<span class="label label-default">异步队列</span> ';
		html += '<span class="label label-info">' + (other.async || 0) + '</span> ' 
		html += '</div></div>';

		html += '<div class="col-md-3" style="margin-bottom: 4px;font-size:16px;"><div>';
		html += '<span class="label label-default">流量统计</span> ';
		html += '<span class="label label-success">' + KMG(count['fetch_kb']) + '</span> '; 
		html += '<span class="label label-info">' + KMG(number['fetch_kb']) + '</span> '; 
		html += '</div></div>';

		$('#counts').html(html);
	}

	function update(number) {
		console.log(number);
		for (var i = 0; i < 59; i += 1) {
			for (var j = 0; j < keys.length; j += 1) {
				datas[keys[j]].data[i][1] = datas[keys[j]].data[i + 1][1];
			}
		}
		for (var j = 0; j < keys.length; j += 1) {
			datas[keys[j]].data[59][1] = number[keys[j]] || 0;
		}
		draw();
	}

	function interval() {
		$.getJSON(dataurl, {}, function (data) {
			update(data.number);
			updateCounts(data.count, data.number, data.doing, data.other);
		});
	}

	setInterval(interval, 1000);
});