$(document).ready(function() {
    $("a.comment").each(function(){
      $(this).on("click",function(){
        var id = $(this).attr('id');
        $.ajax({
            url: '/_comment',
            data:{ 'answer_id' : id},
            method: 'get',
            dataType: 'json'
        }).done(function(response){
            if (response.result)  {
                if ($('div#'+id + '-comment').is(":empty")) {
                    $("html,body").animate({scrollTop:$('div#'+id + '-comment').offset().top},600);
                    $('div#'+id + '-comment').append(response.comment_html);
                    $('div#'+id + '-comment').append(response.page_html);
                    for (var i=0;i<response.comments_id.length;i++)
                        {
                            $('div#'+id + '-comment').find('div#comment-'+response.comments_id[i]).append(moment(response.comments_timestamp[i]).fromNow());
                        };
                    }
                else{
                    $('div#'+id + '-comment').empty();
                }
            }
        });
      });
});

$("div.comment-content-all").on("click","a.comment-page",function(){
  var page = $(this).attr('id');
  var text = $(this).closest('div.comment-content-all').attr('id').split('-');
  var id = text[0];
  if($(this).attr('id') != "disabled"){
    $.ajax({
            url: '/_comment',
            data:{ 'answer_id' : id,
                    'page' : page},
            method: 'get',
            dataType: 'json'
    }).done(function(response){
                if (response.result) {
                    $("html,body").animate({scrollTop:$('div#'+id + '-comment').offset().top},0);
                    $('div#'+id + '-comment').empty();
                    $('div#'+id + '-comment').append(response.comment_html);
                    $('div#'+id + '-comment').append(response.page_html);
                    for (var i=0;i<response.comments_id.length;i++)
                        {
                           $('div#'+id + '-comment').find('div#comment-'+response.comments_id[i]).append(moment(response.comments_timestamp[i]).fromNow());
                        };
                }
            });
  };
});

$("div.comment-content-all").on("click","#comment-submit",function(){
  var text = $(this).closest('div.comment-content-all').attr('id').split('-');
  var id = text[0];
  var comment = $(this).siblings('textarea').val();
  if(comment){
  $.getJSON('/_add_comment',
                { answer_id:id,
                 comment:comment },
                function(json) {
                    if (json.result) {
                        $('div#'+id + '-comment').empty();
                        $("html,body").animate({scrollTop:$('div#'+id + '-comment').offset().top},600);
                        $('div#'+id + '-comment').append(json.comment_html);
                        $('div#'+id + '-comment').append(json.page_html);
                        for (var i=0;i<response.comments_id.length;i++)
                            {
                                $('div#'+id + '-comment').find('div#comment-'+response.comments_id[i]).append(moment(response.comments_timestamp[i]).fromNow());
                            };
                    }else{
                        $('#comment-message-login').modal('show');
                    };


           });
  }else{
    $('#comment-message-content').modal('show');
  }
});
});