$(function() {
        $("#updates").accordion({ heightStyle: "content", collapsible: true });
        $("#case-description").accordion({ heightStyle: "content", collapsible: true });

    });


$(function() {
        $('#show-client-information-toggle').click(function() {
            if (!$(this).data('clicked')) {
                $(this).data('clicked', true);
                $(this).text('Show client information');
                $('#client-information').toggle('drop');
                $('title').text('Case details');
            } else {
                $(this).data('clicked', false);
                $(this).text('Hide client information');
                $('#client-information').toggle('drop');
                $('title').text(clientName); // clientName is global var declared in template
            }
        });
});