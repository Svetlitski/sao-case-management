$(function() {
        $("#updates").accordion({ heightStyle: "content", collapsible: true });
        $("#case-description").accordion({ heightStyle: "content", collapsible: true });
        $clientInformation = $('#info-block');
        originalWidth = $clientInformation.outerWidth(); //deliberately global


    });


$(function() {
        $('#show-client-information-toggle').click(function() {
            if (!$(this).data('clicked')) {
                $(this).data('clicked', true);
                $(this).children().first().attr('class', 'fa fa-angle-right');
                // $clientInformation = $('#client-information')
                $('#update-client-info-btn').fadeOut(175);
                $('#client-information').fadeOut(500);
                $clientInformation.css({'overflow':'hidden', 'white-space': 'nowrap'})
                $clientInformation.animate({width: 20})
                $('title').text('Case details');
            } else {
                $(this).data('clicked', false);
                $(this).children().first().attr('class', 'fa fa-angle-left');
                $('#client-information').fadeIn(500);
                $('#update-client-info-btn').fadeIn(200);
                
                $clientInformation.animate({width: 480});//$clientInformation.css({'overflow': 'visible', 'white-space': 'normal','width': 'auto'}));
                // $clientInformation.css({'overflow': 'visible', 'white-space': 'normal', 'width': 'auto'});
                $('title').text(clientName); // clientName is global var declared in template
            }
        });
});