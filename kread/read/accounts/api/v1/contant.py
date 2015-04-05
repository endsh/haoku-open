# coding: utf-8
from __future__ import unicode_literals
from accounts.sdk.contant import *


M(ACCOUNTS_API_START=21000)
# user
M(USERNAME_NULL='用户名不能为空')
M(USERNAME_TOO_SHORT='用户名长度不能小于6个字符')
M(USERNAME_TOO_LONG='用户名长度不能超过18个字符')
M(USERNAME_FORMAT_ERROR='用户名只能包含英文字符，数字或下划线')
M(USERNAME_EXISTS='该用户名已被注册')
M(PASSWORD_NULL='密码不能为空')
M(PASSWORD_TOO_SHORT='密码长度不能小于6个字符')
M(PASSWORD_TOO_LONG='密码长度不能超过18个字符')
M(PASSWORD_FORMAT_ERROR='密码只能包含英文字符，数字或其他可见符号')
M(REPASSWORD_DIFF='两次密码不一致')
M(NEW_PASSWORD_NEED_DIFF='新密码不能和旧密码一样')
M(EMAIL_TOO_LONG='邮箱地址长度不能超过40个字符')
M(EMAIL_FORMAT_ERROR='邮箱地址格式不正确')
M(EMAIL_EXISTS='该邮箱地址已被注册')
M(EMAIL_NOT_FOUND='该邮箱地址还没有注册')
M(ACCOUNT_NOT_EXISTS='帐号不存在')
M(PASSWORD_ERROR='密码错误')
M(INVALID_URL='链接已失效')
# profile
M(SAVE_FAILE="保存失败")

from accounts.sdk.contant import *