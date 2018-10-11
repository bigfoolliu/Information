function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}


$(function () {
    $(".pass_info").submit(function (e) {
        e.preventDefault();

        // TODO 修改密码
        var params = {};
        $(this).serializeArray().map(function (x) {
            params[x.name] = x.value;
        });

        // 取到两次的密码进行比较
        var new_password = params['new_password'];
        var new_password2 = params['new_password2'];

        if(new_password != new_password2){
            alert('两次输入的密码不一致');
            return
        }

        // ajax请求
        $.ajax({
            url: '/user/pass_info',
            type: 'POST',
            contentType: 'application/json',
            headers: {
                'X-CSRFToken': getCookie('csrf_token')
            },
            data: JSON.stringify(params),
            success: function (resp) {
                // 更改密码成功
                if(resp.erron == '0'){
                    alert('密码更改成功');
                    window.location.reload()
                }else{
                    alert(resp.errmsg)
                }
            }
        })
    })
});