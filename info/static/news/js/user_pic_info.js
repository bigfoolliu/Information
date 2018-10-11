function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}


$(function () {
    $(".pic_info").submit(function (e) {
        e.preventDefault()

        //TODO 上传头像
        // 此处使用的ajaxSubmit等同于submit和ajax的结合体
        // ajax负责发送请求和回调监听
        // form表单负责提交数据

        $(this).ajaxSubmit({
            url: '/user/pic_info',
            type: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrf_token')
            },
            success: function (resp) {
                // 头像上传成功
                // 将各个显示头像的位置更改
                if(resp.erron == '0'){
                    $('.now_user_pic').attr('src', resp.data.avatar_url);
                    $('.user_center_pic>img', parent.document).attr('src', resp.data.avatar_url);
                    $('.user_login>img', parent.document).attr('src', resp.data.avatar_url);
                }else{
                    alert(resp.errmsg)
                }
            }
        })
    })
});
