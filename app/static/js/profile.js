var markers = [];
var map;

function initMap() {
    map = new google.maps.Map(document.getElementById('map'), {
        center: {lat: 25, lng: 0},
        zoom: 2,
        mapTypeId: 'hybrid'
    });
    addMarkers(locations);
}

function addMarkers(locations) {
    for (i=0; i<locations.length; i++) {
        var pos = new google.maps.LatLng(locations[i].lat, locations[i].lng)
        var marker = new google.maps.Marker({
            position: pos,
            map: map,
            title: locations[i].name
        });
        markers.push(marker)
    }
}

function clearMarkers() {
    for (var i = 0; i < markers.length; i++) {
            markers[i].setMap(null)
    }
    markers = [];
}

// Shows markers according to tab clicked
$('.pill-element').click(() => {
    view = $(this).attr('id');
    $(this).siblings().removeClass('active');
    $(this).addClass('active');
    $.ajax({
        type: 'POST',
        url: '/change-map',
        data: {
            view: view
        }
    }).done((response) => {
        clearMarkers();
        addMarkers(response);
    }).fail((error) => {
        console.log(error);
    });
});