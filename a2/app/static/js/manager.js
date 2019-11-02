$(document).ready(function() {

    console.log("caonima, ready")

    $('#addBtn').on("click", function() {
        console.log("add onclick")
        addInstance()
    });

    $('#shrinkBtn').on("click", function() {
        console.log("shrink onclick")
        shrinkInstance()
    })

    $('#deleteBtn').on("click", function() {
        console.log("delete onclick")
        deleteAll()
    })

    $('#stopBtn').on("click", function() {
        console.log("stop onclick")
        stopAll()
    })
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

function shrinkInstance() {
    console.log("shrink one")
    $.ajax({
        type: 'POST',
        url: '/shrink',
        data: '',
        contentType: false,
        success: function(data) {
            
        }
    })
}

function deleteAll() {
    console.log("it's your choice to delete all")
}

function stopAll() {
    console.log("it's your choice to stop all")
}