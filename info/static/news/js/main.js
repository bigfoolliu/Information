$(function(){

	// 打开登录框
	$('.login_btn').click(function(){
        $('.login_form_con').show();
	});
	
	// 点击关闭按钮关闭登录框或者注册框
	$('.shutoff').click(function(){
		$(this).closest('form').hide();
	});

    // 隐藏错误
    $(".login_form #mobile").focus(function(){
        $("#login-mobile-err").hide();
    });
    $(".login_form #password").focus(function(){
        $("#login-password-err").hide();
    });

    $(".register_form #mobile").focus(function(){
        $("#register-mobile-err").hide();
    });
    $(".register_form #imagecode").focus(function(){
        $("#register-image-code-err").hide();
    });
    $(".register_form #smscode").focus(function(){
        $("#register-sms-code-err").hide();
    });
    $(".register_form #password").focus(function(){
        $("#register-password-err").hide();
    });


	// 点击输入框，提示文字上移（*）
    $('.form_group').on('click',function(){
    $(this).children('input').focus()
    });

    $('.form_group input').on('focusin',function(){
        $(this).siblings('.input_tip').animate({'top':-5,'font-size':12},'fast');
        $(this).parent().addClass('hotline');
    });

	

	// 输入框失去焦点，如果输入框为空，则提示文字下移
	$('.form_group input').on('blur focusout',function(){
		$(this).parent().removeClass('hotline');
		var val = $(this).val();
		if(val=='')
		{
			$(this).siblings('.input_tip').animate({'top':22,'font-size':14},'fast');
		}
	});


	// 打开注册框
	$('.register_btn').click(function(){
		$('.register_form_con').show();
		generateImageCode()
	});


	// 登录框和注册框切换
	$('.to_register').click(function(){
		$('.login_form_con').hide();
		$('.register_form_con').show();
        generateImageCode()
	});

	// 登录框和注册框切换
	$('.to_login').click(function(){
		$('.login_form_con').show();
		$('.register_form_con').hide();
	});

	// 根据地址栏的hash值来显示用户中心对应的菜单
	var sHash = window.location.hash;
	if(sHash!=''){
		var sId = sHash.substring(1);
		var oNow = $('.'+sId);		
		var iNowIndex = oNow.index();
		$('.option_list li').eq(iNowIndex).addClass('active').siblings().removeClass('active');
		oNow.show().siblings().hide();
	}

	// 用户中心菜单切换
	var $li = $('.option_list li');
	var $frame = $('#main_frame');

	$li.click(function(){
		if($(this).index()==5){
			$('#main_frame').css({'height':900});
		}
		else{
			$('#main_frame').css({'height':660});
		}
		$(this).addClass('active').siblings().removeClass('active');
		$(this).find('a')[0].click()
	});

    // TODO 登录表单提交
    $(".login_form_con").submit(function (e) {

        // TODO: 注意此处将默认的提交表单请求进行了阻止
        e.preventDefault();

        var mobile = $(".login_form #mobile").val();
        var password = $(".login_form #password").val();

        if (!mobile) {
            $("#login-mobile-err").show();
            return;
        }

        if (!password) {
            $("#login-password-err").show();
            return;
        }

        // 组织登录请求参数
        var params = {
            'mobile': mobile,
            'password': password
        };

        // 发起登录请求
        $.ajax({
            url: '/passport/login',
            type: 'POST',
            data: JSON.stringify(params),
            contentType: 'application/json',
            dataType: 'json',
            headers: {
                'X-CSRFToken': getCookie('csrf_token')
            },
            // 请求成功的回调函数
            success: function (resp) {
                if (resp.erron == "0") {
                    // 返回成功,刷新页面
                    location.reload();
                }else{
                    $('#login-password-err').html(resp.errmsg);
                    $('#register-password-err').show()
                }
            }

        })

    });


    // TODO 注册按钮点击
    $(".register_form_con").submit(function (e) {
        // 阻止默认提交操作
        e.preventDefault();

		// 取到用户输入的内容
        var mobile = $("#register_mobile").val();
        var smscode = $("#smscode").val();
        var password = $("#register_password").val();

		if (!mobile) {
            $("#register-mobile-err").show();
            return;
        }
        if (!smscode) {
            $("#register-sms-code-err").show();
            return;
        }
        if (!password) {
            $("#register-password-err").html("请填写密码!");
            $("#register-password-err").show();
            return;
        }

		if (password.length < 6) {
            $("#register-password-err").html("密码长度不能少于6位");
            $("#register-password-err").show();
            return;
        }

        // TODO: 发起注册请求
        var params = {
            'mobile': mobile,
            'smscode': smscode,
            'password': password
        };

        // 发起注册请求
        $.ajax({
            url: '/passport/register',
            type: 'POST',
            // 将js对象转换为json字符串
            data: JSON.stringify(params),
            // 告知后端发送的数据类型为json
            contentType: 'application/json',
            // 设置接受后端数据为json格式
            dataType: 'json',
            //
            headers: {
              'X-CSRFToken' : getCookie('csrf_token')
            },
            success: function(resp) {
                // 回调函数,即当响应成功之后执行
                if(resp.errno == '0'){
                    // 注册成功,刷新页面从而将表单隐藏
                    window.location.reload()
                }else{
                    // 展示错误信息
                    $('#register-password-err').html(resp.errmsg);
                    $('#register-password-err').show()
                }
            }
        })

    })
});

// 定义的图片验证码的编号
var imageCodeId = "";

// TODO 生成一个图片验证码的编号，并设置页面中图片验证码img标签的src属性
function generateImageCode() {
    // 首先生成一个唯一的uuid编号
    imageCodeId = generateUUID();
    // 拼接验证码的url地址,地址中携带uuid编号传给服务器存储,用于之后的图片验证码
    var imageCodeUrl = '/passport/image_code?code_id=' + imageCodeId;
    // 设置html页面中的图片验证码img标签的src属性,从而可以有不同的图片验证码
    // 利用jq语法
    $('.get_pic_code').attr('src', imageCodeUrl)
}

// 发送短信验证码
function sendSMSCode() {
    // 校验参数，保证输入框有数据填写
    $(".get_code").removeAttr("onclick");
    var mobile = $("#register_mobile").val();
    if (!mobile) {
        $("#register-mobile-err").html("请填写正确的手机号！");
        $("#register-mobile-err").show();
        $(".get_code").attr("onclick", "sendSMSCode();");
        return;
    }
    var imageCode = $("#imagecode").val();
    if (!imageCode) {
        $("#image-code-err").html("请填写验证码！");
        $("#image-code-err").show();
        $(".get_code").attr("onclick", "sendSMSCode();");
        return;
    }

    // TODO 发送短信验证码
    //准备发送给后端的json数据对象,包括手机号,输入的图片验证码,uuid
    var params = {
        'mobile': mobile,
        'image_code': imageCode,
        'image_code_id': imageCodeId
    };

    //发送ajax请求
    $.ajax({
        url: '/passport/sms_code',
        type: 'POST',
        //将js对象转为json数据格式,注意使用该函数
        data: JSON.stringify(params),
        //告诉后端发送的数据类型是json格式
        contentType: 'application/json',
        //接收数据类型也是json格式
        dataType: 'json',
        headers: {
             "X-CSRFToken" : getCookie("csrf_token")
         },
        success:function (resp) {
            //发送短信成功的回调函数,参数resp为前端自定义
            if (resp.errno == 0){
                //发送短信成功,倒计时成功60秒
                var num = 60;
                //设置一个计时器
                var t =setInterval(function () {
                    if (num == 1){
                        //如果计时器到最后,清除计时器对象
                        clearInterval(t);
                        //将点击获取验证码的按钮展示的文本恢复成原始文本
                        $('.get_code').html('获取验证码');
                        //点击按钮的onclick事件属性恢复
                        $('.get_code').attr('onclick', 'sendSMSCode();');
                    }else{
                        num -= 1;
                        //展示倒计时信息
                        $('.get_code').html(num + '秒');
                    }
                }, 1000)
            }else{
                //发送短信验证码异常
                //后端出现异常,将错误信息展示到前端页面
                $('#register-sms-code-err').html(resp.errmsg);
                $('#register-sms-code-err').show();
                //将点击按钮的onclick恢复
                $('.get_code').attr('onclick', 'sendSMSCode();');

                if (resp.errno == '4004'){
                    //验证码填写错误,需要重新填写
                    //调用图片生成图片的方法,重新生成一张新的图片
                    generateImageCode()
                }
            }
        }
    })

}

// 调用该函数模拟点击左侧按钮
function fnChangeMenu(n) {
    var $li = $('.option_list li');
    if (n >= 0) {
        $li.eq(n).addClass('active').siblings().removeClass('active');
        // 执行 a 标签的点击事件
        $li.eq(n).find('a')[0].click()
    }
}

// 一般页面的iframe的高度是660
// 新闻发布页面iframe的高度是900
function fnSetIframeHeight(num){
	var $frame = $('#main_frame');
	$frame.css({'height':num});
}

function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

function generateUUID() {
    var d = new Date().getTime();
    if(window.performance && typeof window.performance.now === "function"){
        d += performance.now(); //use high-precision timer if available
    }
    var uuid = 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
        var r = (d + Math.random()*16)%16 | 0;
        d = Math.floor(d/16);
        return (c=='x' ? r : (r&0x3|0x8)).toString(16);
    });
    return uuid;
}

// 退出登录
function login_out() {
    // 发起注册请求
    $.ajax({
        url: '/passport/login_out',
        type: 'POST',
        // data:,
        contentType: 'application/json',
        // dataType: '',
        headers: {
            'X-CSRFToken': getCookie('csrf_token')
        },
        success: function (resp) {
            if (resp.errno == '0'){
                // 返回成功,刷新页面
                location.reload()
            }else{
                //
            }
        }

    })
}