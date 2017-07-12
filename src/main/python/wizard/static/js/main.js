$(document).ready(function() {
    var state = 0;
    $('html').on('keydown', function(event) {
        console.log(event.key)
        if ($(event.target).attr('id') === 'name') return true;
        var keyPressed = event.key;
        switch(keyPressed) {
        default:
            switch(keyPressed.toLowerCase()) {
                case 'q':
                  $.get('/say?text=hello');
                  break;
                case 'w':
                  $.get('/say?text=goodbye ')
                  break;
            }
        }
    });
});
