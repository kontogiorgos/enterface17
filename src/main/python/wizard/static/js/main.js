$(document).ready(function() {
    var current_page = "dialog"

    function reset() {
        $('.list-group').removeClass('dim');
    }

    var state = 0;
    var combo = [];
    var stop = false;
    $('html').on('keydown', function(event) {
        if (stop) return;
        console.log(event.key)
        if ($(event.target).attr('id') === 'name') return true;
        var keyPressed = event.key.toLowerCase();
        combo.push(keyPressed);
        console.log(combo.sort().join('-') + ' ' + modifier + ', ' + current_page)

        if (combo.length == 2) {
            var modifier = null;
            if (combo.indexOf('alt') !== -1){
                modifier = 'support';
            } else if (combo.indexOf('control') !== -1){
                modifier = 'defend';
            } else if (combo.indexOf('shift') !== -1){
                //console.log(current_page.indexOf('small-talk'))
                if(current_page.indexOf('small-talk') !== -1){
                    modifier = 'small_talk'
                }else if(current_page.indexOf('dialog') !== -1){
                    modifier = 'accuse';
                }
            }

            if (modifier) {
                var participant = combo.filter(item => ['alt', 'control', 'shift','meta'].indexOf(item) === -1)[0]
                switch(participant) {
                    case '§':
                    case '±':
                      $.get(`/dialog_act?action=${modifier}&participant=general`)
                      break;
                    case '0':
                    case 'º':
                    case ')':
                    case '=':
                    case '≠':
                      $.get(`/dialog_act?action=${modifier}&participant=self`)
                      break;
                    case '1':
                    case '¡':
                    case '!':
                    case '':
                      $.get(`/dialog_act?action=${modifier}&participant=black`)
                      break;
                    case '2':
                    case '™':
                    case '@':
                    case '"':
                      $.get(`/dialog_act?action=${modifier}&participant=brown`)
                      break;
                    case '3':
                    case '£':
                    case '#':
                    case '€':
                      $.get(`/dialog_act?action=${modifier}&participant=orange`)
                      break;
                    case '4':
                    case '¢':
                    case '$':
                    case '£':
                      $.get(`/dialog_act?action=${modifier}&participant=blue`)
                      break;
                    case '5':
                    //case '§':
                    case '^':
                    case '%':
                    case '‰':
                      $.get(`/dialog_act?action=${modifier}&participant=pink`)
                      break;
                    case '6':
                    case '¶':
                    case '&':
                    case '¶':
                      $.get(`/dialog_act?action=${modifier}&participant=white`)
                      break;
                }

            }

        }

        if (current_page.indexOf('argue-vote') !== -1){
            console.log('bone'+ ',' + keyPressed)
            switch(keyPressed){
                case '§':
                    $.get(`/dialog_act?action=summary`)
                    break;
                case '1':
                    $.get(`/dialog_act?action=vote&participant=black`)
                    break;
                case '2':
                    $.get(`/dialog_act?action=vote&participant=brown`)
                    break;
                case '3':
                    $.get(`/dialog_act?action=vote&participant=orange`)
                    break;
                case '4':
                    $.get(`/dialog_act?action=vote&participant=pink`)
                    break;
                case '5':
                    $.get(`/dialog_act?action=vote&participant=blue`)
                    break;
                case '6':
                    $.get(`/dialog_act?action=vote&participant=white`)
                    break;
            }
        }


        switch(combo.sort().join('-')) {
            case 'q':
              $.get('/say?text=yes');
              break;
            case 'w':
              $.get('/say?text=no')
              break;
            case 'e':
              $.get('/say?text=maybe')
              break;
            case 'shift':
              $('.list-group:not(#accuse)').addClass('dim');
              break;
            case 'control':
              $('.list-group:not(#defend)').addClass('dim');
              break;
            case 'alt':
              $('.list-group:not(#support)').addClass('dim');
              break;

        }
    });
    $('html').on('keyup', function(event) {
        combo = [];
        stop = false;
        reset();
    });

    $(".change-pane").on("click", function() {
        $(".tab-content .tab-pane").removeClass("active")
        $("#" + $(this).data("page")).addClass("active")
        current_page = $(this).data("page")
    })
});
