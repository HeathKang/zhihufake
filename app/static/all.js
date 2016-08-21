var page = 2;

$('button#btn-questions').click(function () {
    $.ajax({
        url: '/_load_questions?page=' + page + '&content=all',
        method: 'post',
        dataType: 'json'
    }).done(function(response){
        if (response.result) {
            $('div.post').append(response.html);
            page++;
            for (var i=0;i<response.posts.length;i++)
            {
             $("div#" + response.post_id[i]).append(moment(response.posts[i]).fromNow() );
             };
        }
    });
});

$('button#btn-answers').click(function () {
    $.ajax({
        url: '/_load_answers?page=' + page + '&content=all',
        method: 'post',
        dataType: 'json'
    }).done(function(response){
        if (response.result) {
            $('div.answer').append(response.html);
            page++;
            for (var i=0;i<response.answers.length;i++)
            {
             $("div#answer-" + response.answer_id[i]).append(moment(response.answers[i]).fromNow() );
             };
             $(".search-answer-answer").each(function()
				{ var maxwidth=120;
				 if($(this).text().length>maxwidth){
				 $(this).text($(this).text().substring(0,maxwidth));
				$(this).html($(this).html()+'...');
				}
			});
        }
    });
});

$(document).ready(function(){
    $(".search-answer-answer").each(function()
        { var maxwidth=120;
         if($(this).text().length>maxwidth){
         $(this).text($(this).text().substring(0,maxwidth));
        $(this).html($(this).html()+'...');
        }
    });
 });