$(document).ready(function(){
    $(".search-answer-answer").each(function()
        { var maxwidth=120;
         if($(this).text().length>maxwidth){
         $(this).text($(this).text().substring(0,maxwidth));
        $(this).html($(this).html()+'...');
        }
    });
 });