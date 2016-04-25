/**
    Work out what the current configuration is and setup the map
 **/
var mapControls = {
    showSelector: $('.controls #show-selector'),
    selectAreaButton: $('.controls #select-area').hide(),
    deselectAreaButton: $('.controls #deselect-area').hide(),
    trackButton: $('.controls input[name="track-position"]'),
    mapButtons: $('.selector-control'),
    errors: $('.map-errors'),
    markerClass: Markers[$('#map-container').data('marker')] || Marker,
    addressHandler: MarkerHandler[$('#map-container').data('address-handler')]
}

/**
    Set up the show selector button to toggle the selector
 **/
mapControls.showSelector.click(function(){
    mapControls.errors.text('');
    if(mapControls.addressHandler.locationFilter.isEnabled()){
        mapControls.mapButtons.hide()
        mapControls.addressHandler.locationFilter.disable()
    } else {
        mapControls.mapButtons.show();
        mapControls.addressHandler.showLocationFilter();
    }
    return false;
});

/** if an address handler was added, set it up and initialise the map **/
if (mapControls.addressHandler) {
    mapControls.addressHandler.init();

    mapControls.selectAreaButton.click(function(){
        mapControls.addressHandler.selectArea();
    });

    mapControls.deselectAreaButton.click(function(){
        mapControls.addressHandler.deselectArea();
    });

    var watchTracker = null;
    mapControls.trackButton.click(function(){
        if (watchTracker != null) {
            navigator.geolocation.clearWatch(watchTracker);
            watchTracker = null;
        } else {
            watchTracker = navigator.geolocation.watchPosition(function(position, a, b, c) {
                    map.panTo([position.coords.latitude, position.coords.longitude]);
                    map.setZoom(20);
                },
                function(error) {
                    switch(error.code) {
                        case error.PERMISSION_DENIED:
                            console.log("User denied the request for Geolocation.")
                            break;
                        case error.POSITION_UNAVAILABLE:
                            console.log("Location information is unavailable.")
                            break;
                        case error.TIMEOUT:
                            console.log("The request to get user location timed out.")
                            break;
                        case error.UNKNOWN_ERROR:
                            console.log("An unknown error occurred.")
                            break;
                    }
                    mapControls.trackButton.prop('checked', false);
            });
        }
        mapControls.trackButton.prop('checked', watchTracker != null);
    });
}
