$(function(){
    $("button#follow").click(function(){
        var classname=$(this).attr("class");
        var username=$("div.username").attr('id');
        var followers_count=parseInt($("#follower").text());
        if(classname=='following'){
            $("button#follow").attr("class","unfollow");
            $("button#follow").text("取消关注");
            $.getJSON('/_follow',
                {username:username},
                function() {
                    $("#follower").text(followers_count + 1);
                });

            }
        else{
            $("button#follow").attr("class","following");
            $("button#follow").text("关注");
            $.getJSON('/_unfollow',
                {username:username},
                function(json) {
                    $("#follower").text(followers_count - 1);
            });
        }
    });
});