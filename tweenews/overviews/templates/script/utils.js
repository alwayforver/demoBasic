$(document).ready(function() {
    $('.expandable').readmore({
      speed: 75,
      maxHeight: 200,
    });

    $("#content_table").tablesorter();

    $("#advanced-search").click(function() {
        $("#search-form").hide();
        $( "#advanced-search-form" ).slideDown( "slow", function() {
            $( "#id_title" ).focus();
        });
    });

    $("#advanced-cancel").click(function() {
      $( "#advanced-search-form" ).slideUp( "slow", function() {
        $("#search-form").show();
        $( "#q" ).focus();
      });
    });
});