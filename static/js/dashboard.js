$(document).ready(function () {

    var intervalId = window.setInterval(function () {
        run_ajax()
    }, 1000);
});

function run_ajax() {

    $.ajax({
        type: "GET",
        dataType: 'text',
        url: "/widget_broadcast",
        success: function (data) {
            if (data == '') {
                $('#terminal').html(
                    "<div class='small alert alert-info' role='alert'>[!] Output not found" +
                    "</div>"
                )
            } else {
                $("#terminal").html(data)

            }

        },
        error: function (xhr, status, error) {
            $('#terminal').html("<span class='text-danger'>An error occured while refreshing Terminal data.<br>Check if app is running...</span>" +
                "<span class='text-info'><br>" + error + "</span>"
            )
        }
    });
}

