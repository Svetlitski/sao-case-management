$(function() {
        $('#show-all-cases-toggle').click(function() {
            if (!$(this).data('clicked')) {
                $(this).data('clicked', true);
                $(this).text('Show only open cases');
                $('#case-list-page-title').text('All cases');
                $('.closed-case').each(function() {
                    $(this).addClass('closed-case-visible');
                    $(this)[0].onclick = null;
                    $(this).off('click')
                    $(this).on('click', function(e) {
                        if (confirm("This case is closed. You may view it, but you cannot make any changes or additions to the case record without reopening the case.")) {
                            location.href = $(this).attr("href");
                        } else {
                            e.preventDefault();
                        }
                    });
                });
            } else {
                $(this).data('clicked', false);
                $(this).text('Show all cases');
                $('#case-list-page-title').text('Open cases')
                $('.closed-case').each(function() { $(this).removeClass("closed-case-visible") });
            }
        });
    });