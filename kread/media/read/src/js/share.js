
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