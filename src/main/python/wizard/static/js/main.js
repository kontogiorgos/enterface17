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
                  $.get('/say?text=good bye')
                  break;
                case 'a':
                  $.get('/accuse?participant=1')
                  break;
                case 's':
                  $.get('/accuse?participant=2')
                  break;
                case 'd':
                  $.get('/accuse?participant=3')
                  break;
                case 'f':
                  $.get('/accuse?participant=4')
                  break;
                case 'g':
                  $.get('/accuse?participant=5')
                  break;
                case 'h':
                  $.get('/accuse?participant=6')
                  break;
            }
        }
    });
});
