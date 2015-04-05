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
