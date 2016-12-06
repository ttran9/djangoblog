$(document).ready(function() {
    $("#register_userName").focusout(function() {
        var entered_user_name = $("#register_userName").val();
        var csrf_token = getCookie('csrftoken');
        $.ajax({
            url: "/checkUserName/",
            type : "POST",
            dataType: "json",
            data : {
                entered_user_name : entered_user_name,
                csrfmiddlewaretoken: csrf_token
                },
            success : function(response) {
                $('#registration_error').html(response.server_message);
                $('#register_button').attr("disabled", response.is_disabled);
            },
            error : function() {
                $('#registration_error').html('server could not perform the check');
            }
        });
        return false;
    });
});

// using jQuery
function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
