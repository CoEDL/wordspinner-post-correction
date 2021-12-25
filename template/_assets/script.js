$(document).ready(function(){
  $(".entryAudio" ).click(function() {
    var url = $(this).data("file");
    $( "#wsumarcs-dummycat" ).html('<embed src=\"' + url + '\" hidden=\"true\" autostart=\"true\" loop=\"false\" />');
  });
});
