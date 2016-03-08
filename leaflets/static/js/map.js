var map = L.map('map-container').setView([50.223262, 19.070912], 16);
L.tileLayer.provider('OpenStreetMap.Mapnik').addTo(map);

var params = {
    north: 50.226828,
    west: 19.056873,
    south: 50.217513,
    east: 19.084700
};

var markers = Array();
$.get('addresses/list', params, function(data) {
    map.fitBounds(
        $.map(data, function(address, addr_id) {
            var colours = {
                color: 'red',
                fillColor: '#f03',
                fillOpacity: 0.5
            };
            var position = [address.lat, address.lon],
                marker = L.circle(position, 5, colours)
                           .bindPopup(
                                address.street + ' ' + address.house + ',<br>' +
                                address.postcode + ' ' + address.town
                           ).addTo(map);
            markers.push(marker);
            return position;
        })
    );
});