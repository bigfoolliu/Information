function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

$(function(){
    $(".news_review").submit(function (e) {
        e.preventDefault();

        // TODO 新闻审核提交
        var params = {};
        // 获取到所有参数
        $(this).serializeArray().map(function (x) {
            params[x.name] = x.value;
        });
        // 取到具体参数
        var action = params['action'];
        var news_id = params['news_id'];
        var reason = params['reason'];
        if(action == 'reject' && !reason){
            alert('请输入拒绝原因');
            return
        }
        // 组织参数
        params = {
           'action': action,
           'news_id': news_id,
           'reason': reason
        }

        $.ajax({
            url: '/admin/news_review_detail',
            type: 'POST',
            contentType: 'application/json',
            headers: {
                'X-CSRFToken': getCookie('csrf_token')
            },
            data: JSON.stringify(params),
            success: function (resp) {
                // 提交审核成功
                if(resp.erron == '0'){
                    // 返回上一页并刷新数据
                    location.href = document.referrer
                }else{
                    alert(resp.errmsg)
                }

            }
        })

    })
});

// 点击取消，返回上一页
function cancel() {
    history.go(-1)
}