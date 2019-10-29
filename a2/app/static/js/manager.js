$(document).ready(function() {

    console.log("caonima, ready")

    $('#addBtn').on("click", function(){
        console.log("onclick")
        addInstance()
    });
})

function addInstance() {
    console.log("add one")
    $.ajax({
        type: 'POST',
        url: '/add',
        data: '',
        contentType: false,
        success: function(data) {
            data = JSON.parse(data)
            console.log(data)
        }
    });
}