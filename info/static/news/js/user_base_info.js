function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

$(function () {

    $(".base_info").submit(function (e) {
        e.preventDefault();

        var signature = $("#signature").val();
        var nick_name = $("#nick_name").val();
        var gender = $(".gender").val();

        if (!nick_name) {
            alert('请输入昵称');
            return
        }
        if (!gender) {
            alert('请选择性别')
        }

        // TODO 修改用户信息接口
        var params = {
            'signature': signature,
            'nick_name': nick_name,
            'gender': gender
        };

        $.ajax({
          url: '/user/base_info',
          type: 'POST',
          contentType: 'application/json',
          headers: {
              'X-CSRFToken': getCookie('csrf_token')
          },
          data: JSON.stringify(params),
          success: function (resp) {
              // 用户信息提交成功
              if(resp.erron == '0'){
                  // 更新父窗口内容
                  $('.user_center_name', parent.document).html(params['nick_name']);
                  $('#nick_name', parent.document).html(params['nick_name']);
                  $('.input_sub').blur()
              }else{
                  alert(resp.errmsg)
              }

              // 刷新当前的父页面实现总体刷新
              window.parent.location.reload()
          }
        })
    })
});