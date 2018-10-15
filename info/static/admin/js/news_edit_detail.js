function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

$(function(){
    $(".news_edit").submit(function (e) {
        e.preventDefault();

        // TODO 新闻编辑提交
        $(this).ajaxSubmit({
            beforeSubmit: function (request) {
                // 提交之前对参数进行处理
                for(var i=0; i<request.length; i++){
                    var item = request[i];
                    if(item['name'] == 'content'){
                        item['value'] = tinyMCE.activeEditor.getContent()
                    }
                }
            },
            url: '/admin/news_edit_detail',
            type: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrf_token')
            },
            success: function (resp) {
                // 新闻版式编辑提交成功
                if(resp.erron == '0'){
                    // 返回上一页并刷新数据
                    location.href = document.referrer;
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