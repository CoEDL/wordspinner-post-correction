$(document).ready(function(){
  $(".entryAudio" ).click(function() {
    var url = $(this).data("file");
    $("#dummycat").html('<audio controls autoplay hidden><source src="' + url + '" type="audio/mpeg"></audio>');
  });
});
