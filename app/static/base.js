
$(function() {
    $("a.up").each(function(){
        $(this).bind("click",function(){
            var id = $(this).attr('id');
            var button_class = $("#button-up-" + id).attr("class");
            var span_class = $("#span-up-" + id).attr("class");
            $.getJSON('/_add_agree',
                {answer_id:id},
                function(json) {
                    $("#agree-count-" + id ).text(json.agree_count);
                    if($("#button-up-" + id).hasClass("button-uped")){
                        $("#button-up-" + id).removeClass("button-uped");
                        $("#span-up-" + id).removeClass("vote-uped");
                        }else{
                        $("#button-up-" + id).addClass("button-uped");
                        $("#span-up-" + id).addClass("vote-uped");
                    };

            });
        });
    });
});


$("#searchText").keyup(function(){
    var searchText = $("#searchText").val();
    if(searchText){
        $("ul#searchList").removeClass("hidden");
        $.getJSON('/_search',
                { key:searchText },
                function(json) {
                    var contents = json.post;
                    var user = json.user;
                    var answer = json.answer;
                    var url = json.url;
                    var answers_urls = json.answers_urls;
                    var users_urls = json.user_urls;
                    var search_all_url = json.search_all;
                    $("ul#searchList").empty();
                    if(url == 'None'){
                        $("ul#searchList").append("<li class='list-group-item list-group-item-warning'>" + contents + "</a></li>" );
                    }
                    else{
                        $("ul#searchList").append("<li class='list-group-item list-group-item-info'>问题</li>" );
                        for (var i=0;i<contents.length;i++)
                        {
                           $("ul#searchList").append("<li class='list-group-item search-li'><a  href='" + url[i] + "'>" + contents[i] + "</a></li>" );
                        };
                        for (var j=0;j<answer.length;j++)
                        {
                           $("ul#searchList").append("<li class='list-group-item search-li'><a  href='" + answers_urls[j] + "'>" + answer[j] + "</a></li>" );
                        };
                           $("ul#searchList").append("<li class='list-group-item list-group-item-info'>用户</li>" );
                         for (var k=0;k<user.length;k++)
                        {
                           $("ul#searchList").append("<li class='list-group-item'><a  href='" + users_urls[k] + "'>" + user[k] + "</a></li>" );
                        };
                           $("ul#searchList").append("<li class='list-group-item list-group-item-info'><a  href='" + search_all_url +"'>查看全部结果 <span class='glyphicon glyphicon-forward'></span></a></li>" );

                    }

        });
    }
    if(!searchText){
        $("ul#searchList").empty();
        $("ul#searchList").addClass("hidden");
    }
});


function checksearchForm(form) {
for (var i = 0; i < form.elements.length; i++) {
    if (form.elements[i].type == "text" && form.elements[i].value == "") {
        return false;
        }
    }
return true;
}