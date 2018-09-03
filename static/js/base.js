$(function() { // Puts a colored border under the current page in the navbar
      $page = window.location.pathname;
      if (!$page) {
          $page = 'index.html';
      }
      $("#navbar a").each(function() {
          var $href = $(this).attr('href');
          if (($href == $page) || ($href == '')) {
              $(this).addClass('is_current_page');
          } else {
              $(this).removeClass('is_current_page');
          }
      });
  });