/**
    Work out what the current configuration is
 **/
var markerClasses = {
    'Marker': Markers.Marker,
    'CampaignMarker': Markers.CampaignMarker,
}
var handlerClasses = {
    'DisplaySelector': MarkerHandler.DisplaySelector,
    'AddressAdder': MarkerHandler.AddressAdder,
    'CampaignAddressSelector': MarkerHandler.CampaignAddressSelector
}
var mapControls = {
    showSelector: $('.controls #show-selector'),
    selectAreaButton: $('.controls #select-area').hide(),
    deselectAreaButton: $('.controls #deselect-area').hide(),
    mapButtons: $('.selector-control'),
    errors: $('.map-errors'),
    markerClass: markerClasses[$('#map-container').data('marker')] || Marker,
    addressHandler: handlerClasses[$('#map-container').data('address-handler')]
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
}
