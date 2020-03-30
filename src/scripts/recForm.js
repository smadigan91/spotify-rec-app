function doShare(url) {
//    var selected = document.getElementsByClassName('is-selected')
//    if(selected === undefined || selected.length == 0) {
//        window.alert('No songs selected to share')
//        return
//    }
//    var data = {tracks: []}
//    for (track of selected) {
//        data.tracks.push(track.getAttribute('data-track'))
//    }

    var xhr = new XMLHttpRequest()
    xhr.open('POST', url + '/share', true)
    xhr.setRequestHeader('Content-Type', 'application/json; charset=UTF-8');
    xhr.send(JSON.stringify(data))

    xhr.onreadystatechange = processRequest

    function processRequest(e) {
        if (xhr.readyState == 4 && xhr.status == 201) {
            window.alert('Success!')
        }
        else if (xhr.readyState == 4 && xhr.status == 505) {
            window.alert('No master devices!')
        }
        else if (xhr.readyState == 4 && xhr.status == 506) {
            window.alert('Master devices found but none were active!')
        }
        else if (xhr.readyState == 4 && xhr.status != 201) {
            window.alert('Something went wrong, status was: ' + xhr.status)
        }
    }
}