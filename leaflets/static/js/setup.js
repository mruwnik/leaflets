/**
    Work out what the current configuration is and setup the map
 **/
var mapControls = {
    showSelector: $('.controls #show-selector'),
    selectAreaButton: $('.controls #select-area').hide(),
    deselectAreaButton: $('.controls #deselect-area').hide(),
    trackButton: $('button.controls[name="track-position"]'),
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
        map.locate({setView: true, maxZoom: 20});
        map.locate({maxZoom: 20, watch: true});
    });
}
