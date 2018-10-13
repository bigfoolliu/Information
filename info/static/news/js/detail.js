function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}


$(function(){

    // 每次进入就需要更新评论数量
    updateCommentCount();

    // 打开登录框
    $('.comment_form_logout').click(function () {
        $('.login_form_con').show();
    });

    // 收藏
    $(".collection").click(function () {
        // 点击收藏按钮,向后端发送post请求
        var news_id = $('.collection').attr('data-newsid');
        var action = 'collect';

        // 组织参数
        var params = {
            'news_id': news_id,
            'action': action
        };

        // 发送请求
        $.ajax({
            url: '/news/news_collect',
            type: 'post',
            contentType: 'application/json',
            headers: {
                'X-CSRFToken': getCookie('csrf_token')
            },
            data: JSON.stringify(params),
            success: function (resp) {

                if (resp.erron == '0') {

                    // 收藏成功
                    // 隐藏收藏按钮,显示已收藏按钮
                    $('.collected').show();
                    $('.collection').hide()
                }else if (resp.erron == '4101') {
                    // 用户未登录
                    $('.login_form_con').show();
                }else {
                    alert(resp.errmsg);
                }
            }
        })
       
    });

    // 取消收藏
    $(".collected").click(function () {
        // 点击取消收藏按钮,向后端发送post请求
        var news_id = $('.collected').attr('data-newsid');
        var action = 'cancel_collect';

        // 组织参数
        var params = {
            'news_id': news_id,
            'action': action
        };
        
        // 发送请求
        $.ajax({
            url: '/news/news_collect',
            type: 'post',
            contentType: 'application/json',
            headers: {
                'X-CSRFToken': getCookie('csrf_token')
            },
            data: JSON.stringify(params),
            // 回调函数
            success: function(resp) {

                if(resp.erron == '0'){

                    // 取消收藏成功
                    // 显示收藏按钮
                    $('.collection').show();
                    // 隐藏已收藏按钮
                    $('.collected').hide();
                }else if(resp.erron == '4101'){
                    // 用户未登录
                    $('.login_form_con').show();
                }else {
                    alert(resp.errmsg);
                }

            }
            
        })
     
    });

    // TODO: 评论提交(主评论)
    $(".comment_form").submit(function (e) {
        e.preventDefault();

        // 获取参数
        var news_id = $(this).attr('data-newsid');
        var news_comment = $('.comment_input').val();

        if(!news_comment){
            alert('请输入评论内容!');
            return
        }
        
        // 组织请求参数
        var params = {
            'news_id': news_id,
            'comment': news_comment
        };
        $.ajax({
            url: '/news/news_comment',
            type: 'POST',
            contentType: 'application/json',
            headers: {
                'X-CSRFToken': getCookie('csrf_token')
            },
            data: JSON.stringify(params),
            success: function (resp) {
                if(resp.erron == '0'){
                    // 评论成功
                    var comment = resp.data;
                    // 拼接内容
                    var comment_html = '';
                    comment_html += '<div class="comment_list">';
                    comment_html += '<div class="person_pic fl">';
                    if (comment.user.avatar_url) {
                        comment_html += '<img src="' + comment.user.avatar_url + '" alt="用户图标">'
                    }else {
                        comment_html += '<img src="../../static/news/images/person01.png" alt="用户图标">'
                    }
                    comment_html += '</div>';
                    comment_html += '<div class="user_name fl">' + comment.user.nick_name + '</div>';
                    comment_html += '<div class="comment_text fl">';
                    comment_html += comment.content;
                    comment_html += '</div>';
                    comment_html += '<div class="comment_time fl">' + comment.create_time + '</div>';

                    comment_html += '<a href="javascript:;" class="comment_up fr" data-commentid="' + comment.id + '" data-newsid="' + comment.news_id + '">赞</a>';
                    comment_html += '<a href="javascript:;" class="comment_reply fr">回复</a>';
                    comment_html += '<form class="reply_form fl" data-commentid="' + comment.id + '" data-newsid="' + news_id + '">';
                    comment_html += '<textarea class="reply_input"></textarea>';
                    comment_html += '<input type="button" value="回复" class="reply_sub fr">';
                    comment_html += '<input type="reset" name="" value="取消" class="reply_cancel fr">';
                    comment_html += '</form>';

                    comment_html += '</div>';

                    // 拼接到内容的前面
                    $('.comment_list_con').prepend(comment_html);
                    // 让comment_sub失去焦点
                    $('.comment_sub').blur();
                    // 清空输入框内容
                    $('.comment_input').val('');
                    // 评论完毕更新评论条数
                    updateCommentCount()
                }else{
                    alert(resp.errmsg)
                }
            }
        })

    });

    $('.comment_list_con').delegate('a,input','click',function(){

        var sHandler = $(this).prop('class');

        if(sHandler.indexOf('comment_reply')>=0)
        {
            $(this).next().toggle();
        }

        if(sHandler.indexOf('reply_cancel')>=0)
        {
            $(this).parent().toggle();
        }

        // TODO: 点赞/取消点赞前端接口
        if(sHandler.indexOf('comment_up')>=0)
        {
            var $this = $(this);
            // 点赞/取消点赞行文
            var action = 'add';

            if(sHandler.indexOf('has_comment_up')>=0)
            {
                // 如果当前评论已经是点赞状态,再次点击会进入此代码块,表示取消点赞
                action = 'remove'
            }

            // 评论id
            var comment_id = $(this).attr('data-commentid');
            // 组织请求参数
            var params = {
                'comment_id': comment_id,
                'action': action
            };
            
            $.ajax({
                url: '/news/comment_like',
                type: 'POST',
                contentType: 'application/json',
                headers: {
                    'X-CSRFToken': getCookie('csrf_token')
                },
                data: JSON.stringify(params),
                success: function (resp) {
                    // 点赞/取消点赞成功

                    if(resp.erron == '0'){
                        // 获取当前点赞数目
                        var like_count = $this.attr('data-likecount');

                        if(like_count == undefined){
                            like_count = 0
                        }

                        // 更新点赞按钮图标
                        if(action == 'add'){
                            // 点赞
                            like_count = parseInt(like_count) + 1;
                            $this.addClass('has_comment_up')
                        }else{
                            // 取消点赞
                            like_count = parseInt(like_count) - 1;
                            $this.removeClass('has_comment_up')
                        }

                        // 更新点赞数据
                        $this.attr('data-likecount', like_count);

                        if(like_count <= 0){
                            $this.html('赞')
                        }else{
                            $this.html(like_count)
                        }
                    }else if(resp.erron == '4101'){
                        // 弹出登录框
                        $('.login_form_con').show()
                    }else{
                        // 展示错误
                        alert(resp.errmsg)
                    }
                }
            })
        }

        // 发布评论(子评论)
        if(sHandler.indexOf('reply_sub')>=0)
        {
            var $this = $(this);
            // 新闻id
            var news_id = $this.parent().attr('data-newsid');
            // 父评论id
            var parent_id = $this.parent().attr('data-commentid');
            // 评论内容
            var comment = $this.prev().val();

            // 若评论内容为空
            if(!comment){
                alert('请输入评论内容!');
                return
            }

            // 组织请求参数
            var params = {
                'news_id': news_id,
                'comment': comment,
                'parent_id': parent_id
            };

            $.ajax({
                url: '/news/news_comment',
                type: 'POST',
                contentType: 'application/json',
                headers: {
                    'X-CSRFToken': getCookie('csrf_token')
                },
                data: JSON.stringify(params),
                success: function (resp) {
                    // 子评论评论成功
                    if(resp.erron == '0'){
                        var comment = resp.data;
                        // 拼接内容
                        var comment_html = "";
                        comment_html += '<div class="comment_list">';
                        comment_html += '<div class="person_pic fl">';
                        if (comment.user.avatar_url) {
                            comment_html += '<img src="' + comment.user.avatar_url + '" alt="用户图标">'
                        }else {
                            comment_html += '<img src="../../static/news/images/person01.png" alt="用户图标">'
                        }
                        comment_html += '</div>';
                        comment_html += '<div class="user_name fl">' + comment.user.nick_name + '</div>';
                        comment_html += '<div class="comment_text fl">';
                        comment_html += comment.content;
                        comment_html += '</div>';
                        comment_html += '<div class="reply_text_con fl">';
                        comment_html += '<div class="user_name2">' + comment.parent.user.nick_name + '</div>';
                        comment_html += '<div class="reply_text">';
                        comment_html += comment.parent.content;
                        comment_html += '</div>';
                        comment_html += '</div>';
                        comment_html += '<div class="comment_time fl">' + comment.create_time + '</div>';

                        comment_html += '<a href="javascript:;" class="comment_up fr" data-commentid="' + comment.id + '" data-newsid="' + comment.news_id + '">赞</a>';
                        comment_html += '<a href="javascript:;" class="comment_reply fr">回复</a>';
                        comment_html += '<form class="reply_form fl" data-commentid="' + comment.id + '" data-newsid="' + news_id + '">';
                        comment_html += '<textarea class="reply_input"></textarea>';
                        comment_html += '<input type="button" value="回复" class="reply_sub fr">';
                        comment_html += '<input type="reset" name="" value="取消" class="reply_cancel fr">';
                        comment_html += '</form>';

                        comment_html += '</div>';

                        // 拼接到内容前面
                        $('.comment_list_con').prepend(comment_html);
                        // 清空输入框
                        $this.prev().val();
                        // 关闭子评论框
                        $this.parent().hide();
                        // 更新评论条数
                        updateCommentCount()
                    }else{
                        alert(resp.errmsg)
                    }
                }
            })
        }

    });

    // 关注当前新闻作者
    $(".focus").click(function () {

        var user_id = $(this).attr('data-userid');
        var params = {
            'action': 'follow',
            'user_id': user_id
        };

        $.ajax({
            url: '/news/followed_user',
            type: 'POST',
            contentType: 'application/json',
            headers: {
                'X-CSRFToken': getCookie('csrf_token')
            },
            data: JSON.stringify(params),
            success: function (resp) {
                // 关注当前新闻作者成功
                if(resp.erron == '0'){
                    var count = parseInt($('.follows b').html());
                    count++;
                    $('.follows b').html(count + '');
                    $('.focus').hide();
                    $('.focused').show()
                }else if(resp.erron == '4101'){
                    // 用户未登录,弹出登录框
                    $('.login_form_con').show()
                }else{
                    // 关注失败
                    alert(resp.errmsg)
                }
            }
        })

    });

    // 取消关注当前新闻作者
    $(".focused").click(function () {

        var user_id = $(this).attr('data-userid');
        var params = {
            'action': 'unfollow',
            'user_id': user_id
        };

        $.ajax({
            url: '/news/followed_user',
            type: 'POST',
            contentType: 'application/json',
            headers: {
                'X-CSRFToken': getCookie('csrf_token')
            },
            data: JSON.stringify(params),
            success: function (resp) {
                // 取消关注当前新闻作者成功
                if(resp.erron == '0'){
                    var count = parseInt($('.follows b').html());
                    count--;
                    $('.follows b').html(count + '');
                    $('.focus').hide();
                    $('.focused').show()
                }else if(resp.erron == '4101'){
                    // 用户未登录,弹出登录框
                    $('.login_form_con').show()
                }else{
                    // 关注失败
                    alert(resp.errmsg)
                }
            }
        })

    })
});


// 更新新闻评论条数
function updateCommentCount() {
    var count = $('.comment_list').length;
    $('.comment_count').html(count + '条评论')
}
