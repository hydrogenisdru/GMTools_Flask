/**
 * Created by zouyang on 2017/5/21.
 */
$('.dropdown-toggle').dropdown()

function queryPlayer() {
    // var search_info = $('#search-input').val()
    // $.post($SCRIPT_ROOT + "/gmtools/controls", {info: search_info}, function () {
    //     // window.location.href = $SCRIPT_ROOT + "/gmtools/controls";
    // });
    $('#search_form').submit();
}

function openProfile(uuid) {
    window.location.href = $SCRIPT_ROOT + "/gm/gmtools/profile/" + uuid;
}

function kick(uuid) {
    $.post($SCRIPT_ROOT + "/gm/kick/" + uuid, function () {
        window.location.href = $SCRIPT_ROOT + "/gm/gmtools/controls";
    });
}

function check_activity() {
    $.post($SCRIPT_ROOT + "/gm/gmtools/check_activity", function (resp) {
        var data = eval(resp);
        var table = $('#dataTable3').DataTable();
        table.clear();
        table.rows.add(data).draw();
    });
}

function check_system_mail() {
    $.post($SCRIPT_ROOT + "/gm/gmtools/check_system_mail", function (resp) {
        var data = eval(resp);
        var table = $('#dataTable2').DataTable();
        table.clear();
        table.rows.add(data).draw();
    });
}

function delete_system_mail() {
    var table = $('#dataTable2').DataTable();
    table.rows('.selected').data().each(function (d) {
        $.post($SCRIPT_ROOT + "/gm/gmtools/system_mail_delete", {mailId: d._id}, function (resp) {
            alert(resp);
        });
    });
    table.rows('.selected').remove().draw();
}
