var initialize = function (navigator, user, token, urls) {
    $('#id_login').on('click', function () {
        navigator.id.request();
    });
    navigator.id.watch({
        loggedInUser: user,
        onlogin: function (assertion) {
            $.post(
                urls.login,
                {assertion: assertion, csrfmiddlewaretoken: token}
            ).fail(function () {
                navigator.id.logout();
            }).done(function () {
                window.location.reload();
            });
        },
        onlogout: function () {
            $.get(urls.logout);
        }
    });
};

window.Superlists = {
    Accounts: {
        initialize: initialize
    }
};