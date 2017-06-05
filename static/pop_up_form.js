/**
 * Created by zouyang on 2017/5/19.
 */
$('#exampleModal').on('show.bs.modal', function (event) {
    var button = $(event.relatedTarget) // Button that triggered the modal
    var recipient = button.data('whatever') // Extract info from data-* attributes
    // If necessary, you could initiate an AJAX request here (and then do the updating in a callback).
    // Update the modal's content. We'll use jQuery here, but you could use a data binding library or other methods instead.
    var modal = $(this)
    var content = recipient.split(',')
    if (content.length > 1) {
        modal.find('.modal-title').text('Edit')
        modal.find('#userName').attr('readonly','readonly')
        modal.find('#userName').val(content[0].trim())
        modal.find('#authority').val(content[1].trim())
        modal.find('#authority_div').show()
        modal.find('#submit').val('apply')
    } else {
        modal.find('.modal-title').text('Sign up')
        modal.find('#authority').val('none')
        modal.find('#userName').removeAttr('readonly')
        modal.find('#authority_div').hide()
        modal.find('#submit').val('signup')
    }
    // modal.find('.modal-body input').val(recipient)
})
// $('#editModal').on('show.bs.modal', function (event) {
//     var button = $(event.relatedTarget) // Button that triggered the modal
//     var recipient = button.data('whatever') // Extract info from data-* attributes
//     // If necessary, you could initiate an AJAX request here (and then do the updating in a callback).
//     // Update the modal's content. We'll use jQuery here, but you could use a data binding library or other methods instead.
//     var content = recipient.split(',')
//     var modal = $(this)
//     modal.find('#userName').val(content[0].trim())
//     modal.find('#authority').val(content[1].trim())
// })

function confirmDelete(userId) {
    bootbox.confirm({
        size: "small",
        message: "confirm DELETE?",
        callback: function (result) {
            if (result) {
                $.post($SCRIPT_ROOT + "/delete/" + userId, function () {
                    window.location.href = $SCRIPT_ROOT + "/gmtools/manage";
                });
            }
        }
    });
}

