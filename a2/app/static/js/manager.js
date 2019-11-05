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

function refresh() {
    location.reload();
}

function getLoading() {
    loadingArea = document.createElement('span')
    loadingArea.setAttribute('role', 'status')
    loadingArea.setAttribute('class', 'spinner-border spinner-border-sm')
    return loadingArea
}

function addInstance() {
    area = document.getElementById('addBtn')
    // loadingArea = document.createElement('<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>')
    loadingArea = getLoading()
    area.appendChild(loadingArea)    
    $.ajax({
        type: 'POST',
        url: '/add',
        data: '',
        contentType: false,
        success: function(data) {
            console.log(data)
            let res = JSON.parse(data)
            if(res.success != 1) {
                alert(res.msg)
            }
            location.reload();
        }
    });
}

function shrinkInstance() {
    area = document.getElementById('shrinkBtn')
    loadingArea = getLoading();
    area.appendChild(loadingArea)
    $.ajax({
        type: 'POST',
        url: '/shrink',
        data: '',
        contentType: false,
        success: function(data) {
            console.log(data)
            let res = JSON.parse(data)
            if(res.success != 1) {
                alert(res.msg)
            }
            location.reload();
        }
    })
}

function deleteAll() {
    area = document.getElementById('deleteBtn')
    loadingArea = getLoading();
    area.appendChild(loadingArea)
    alert("it's your choice to delete all")
    $.ajax({
        type: 'POST',
        url: '/delete',
        data: '',
        contentType: false,
        success: function(data) {
            alert("delete succeeded")
            location.reload();
        }
    })
}

function stopAll() {
    area = document.getElementById('stopBtn')
    loadingArea = getLoading();
    area.appendChild(loadingArea)
    alert("it's your choice to stop all")
    window.location.href = "/stop";
    // $.ajax({
    //     type: 'POST',
    //     url: '/stop',
    //     data: '',
    //     contentType: false,
    //     success: function(data) {
    //         console.log(data)
    //         let res = JSON.parse(data)
    //         window.location.href = res.redirect;
    //     }
    // })
}