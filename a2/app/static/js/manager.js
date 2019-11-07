$(document).ready(function() {

    console.log("caonima, ready")

    $('#addBtn').on("click", function() {
        addInstance()
    });

    $('#shrinkBtn').on("click", function() {
        shrinkInstance()
    })

    $('#deleteBtn').on("click", function() {
        deleteAll()
    })

    $('#stopBtn').on("click", function() {
        stopAll()
    })

    $('#configBtn').on("click", function() {
        config()
    })
})

function getLoading() {
    loadingArea = document.createElement('span')
    loadingArea.setAttribute('role', 'status')
    loadingArea.setAttribute('class', 'spinner-border spinner-border-sm')
    return loadingArea
}

function addInstance() {
    area = document.getElementById('addBtn')
    loadingArea = getLoading()
    area.appendChild(loadingArea)
    area.disabled = true
    document.getElementById('shrinkBtn').disabled = true
    document.getElementById('deleteBtn').disabled = true   
    document.getElementById('stopBtn').disabled = true
    $.ajax({
        type: 'POST',
        url: '/add',
        data: '',
        contentType: false,
        success: function(data) {
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
    area.disabled = true   
    document.getElementById('addBtn').disabled = true
    document.getElementById('deleteBtn').disabled = true   
    document.getElementById('stopBtn').disabled = true
    $.ajax({
        type: 'POST',
        url: '/shrink',
        data: '',
        contentType: false,
        success: function(data) {
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
    area.disabled = true   
    document.getElementById('addBtn').disabled = true
    document.getElementById('shrinkBtn').disabled = true   
    document.getElementById('stopBtn').disabled = true
    alert("it's your choice to delete all")
    $.ajax({
        type: 'POST',
        url: '/delete',
        data: '',
        contentType: false,
        success: function(data) {
            alert("delete successfully")
            location.reload();
        }
    })
}

function stopAll() {
    area = document.getElementById('stopBtn')
    loadingArea = getLoading();
    area.appendChild(loadingArea)
    area.disabled = true  
    document.getElementById('addBtn').disabled = true
    document.getElementById('shrinkBtn').disabled = true   
    document.getElementById('deleteBtn').disabled = true 
    alert("it's your choice to stop all")
    window.location.href = "/stop";
}

function config() {
    window.location.href = "/config";
}