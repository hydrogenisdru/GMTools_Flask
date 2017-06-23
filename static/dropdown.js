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