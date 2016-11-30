// validate the registration form.
function registration_validation() {
    var user_name_regex = new RegExp("[a-z0-9_-]{6,35}$");
    var email_regex = new RegExp("^[_A-Za-z0-9-]+(\\.[_A-Za-z0-9-]+)*@[A-Za-z0-9]+(\\.[A-Za-z0-9]+)*(\\.[A-Za-z]{2,})$");
    var userName = document.getElementById("register_userName").value;
    var email = document.getElementById("register_userEmailAddress").value;
    document.getElementById("registration_error").innerHTML = "";

    if(!(user_name_regex.test(userName))) {
        document.getElementById("registration_error").innerHTML =
            "userName must be 6 to 35 characters, and must only have lower case letters, " +
            "numbers, the two characters, '-' and '_'!";
        return false;
    }
    if(!(email_regex.test(email))) {
        document.getElementById("registration_error").innerHTML =
            "email does not follow the proper format ";
        return false;
    }

    return true;
}


// validate the login form
function login_validation() {
    var user_name_regex = new RegExp("[a-z0-9_-]{6,35}$");

    var password_regex = new RegExp("((?=.*\\d)(?=.*[a-z])(?=.*[A-Z])(?=.*[@#$%]).{6,20})");
    var userName = document.getElementById("login_userName").value;
    var password = document.getElementById("login_userPassword").value;

    document.getElementById("login_error").innerHTML =  "";
    if(!(user_name_regex.test(userName)) || !(password_regex.test(password))) {
        document.getElementById("login_error").innerHTML =  "incorrect credentials!";
        return false;
    }
    return true;
}

// validate the password change form
function change_password_validation() {
    var password_regex = new RegExp("((?=.*\\d)(?=.*[a-z])(?=.*[A-Z])(?=.*[@#$%]).{6,20})");
    var password = document.getElementById("user_password").value;
    var passwordVerify = document.getElementById("user_password_verify").value;

    document.getElementById("change_password_error").innerHTML = "";
    if(!(passwordVerify === password)) {
        document.getElementById("change_password_error").innerHTML = "passwords must match";
        return false;
    }
    if(!(password_regex.test(password)) || !(password_regex.test(passwordVerify)) ) {
        document.getElementById("change_password_error").innerHTML = "The password must have at least one " +
            "number, one lower and upper case letter, and one of the special symbols: " + " \'@\', " +
            "\'#\', \'$\', \'%\'" + "<br/>" + "The length must be between 6 to 20 characters!";
        return false;
    }
    return true;
}


