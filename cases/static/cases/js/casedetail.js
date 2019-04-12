$(function() {
        $("#updates").accordion({ heightStyle: "content", collapsible: true });
        $("#case-description").accordion({ heightStyle: "content", collapsible: true });
        $infoBlock = $('#info-block');
        originalWidth = $infoBlock.outerWidth();
        


    });


$(function() {
        $('#show-client-information-toggle').click(function() {
            if (!$(this).data('clicked')) {
                $(this).data('clicked', true);
                $(this).children().first().attr('class', 'fa fa-angle-right');
                $('#update-client-info-btn').fadeOut(175);
                $('#client-information').fadeOut(350);
                $infoBlock.css({'overflow':'hidden', 'white-space': 'nowrap'})
                $('')
                $infoBlock.animate({width: $('#show-client-information-toggle').outerWidth()})
            } else {
                $(this).data('clicked', false);
                $(this).children().first().attr('class', 'fa fa-angle-left');
                $('#client-information').fadeIn(500);
                $('#update-client-info-btn').fadeIn(200);
                $infoBlock.animate({width: originalWidth});
            }
        });
});
