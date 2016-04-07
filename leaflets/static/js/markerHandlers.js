
/**
    The base handler for the map selector
 **/
BaseAddressSelector = function(xsrf) {
    this.xsrf= xsrf || $('[name="_xsrf"]').val();
};
BaseAddressSelector.prototype = {
    locationFilter: new L.LocationFilter().addTo(map)
};
BaseAddressSelector.prototype.currentBounds = function() {
    var bounds = this.locationFilter.getBounds();
    return {
        north: bounds._northEast.lat,
        west: bounds._southWest.lng,
        south: bounds._southWest.lat,
        east: bounds._northEast.lng
    }
};

BaseAddressSelector.prototype.newMarker = function(address) {
    return new Markers.Marker(address);
};
BaseAddressSelector.prototype.init = function() {
    Markers.MarkersGetter(mapControls.markerClass);
};
BaseAddressSelector.prototype.selectArea = function() {};
BaseAddressSelector.prototype.deselectArea = function() {};
BaseAddressSelector.prototype.showLocationFilter = function() {;
    this.locationFilter.enable();
}


/** A simple selector that only displays addresses **/
DisplaySelector = new BaseAddressSelector();


/**
    Handle adding new addresses to the system.
 **/
AddressAdder = new BaseAddressSelector();

AddressAdder.init = function() {
    Markers.MarkersGetter(mapControls.markerClass);
    this.locationFilter.on('change', function(event, a, b) {
        var bounds = event.bounds;
        if(Math.abs(bounds.getNorth()) - Math.abs(bounds.getSouth())
            + Math.abs(bounds.getEast()) - Math.abs(bounds.getWest()) > 0.05) {
            $('.leaflet-zoom-animated g path').attr('fill', 'red');
        } else {
            $('.leaflet-zoom-animated g path').attr('fill', 'black');
        }
    });
};
/**
    Show the location filter.

    Also make sure that its initial size is in the allowed bounds.
 **/
AddressAdder.showLocationFilter = function() {;
    this.locationFilter.enable();
    var bounds = this.locationFilter.getBounds(),
        center = bounds.getCenter();
    bounds._southWest = {lat: center.lat - 0.01, lng: center.lng - 0.015};
    bounds._northEast = {lat: center.lat + 0.01, lng: center.lng + 0.015};
    this.locationFilter.setBounds(bounds);
}
AddressAdder.selectArea = function(boundingBox) {
    var boundingBox = boundingBox || this.currentBounds();
        params = {
            '_xsrf': this.xsrf
        };
    mapControls.errors.text('searching for addresses...');
    return $.post('/addresses/search', $.extend(params, boundingBox), function(results) {
        mapControls.errors.text('');
        Markers.MarkersGetter(Markers.Marker, boundingBox, false);
    }).error(function(error) {
        mapControls.errors.text(error.statusText);
    });
}


/**
 *   Handle selecting addresses while creating a new campaign.
 *
 *   Whenever an area is selected, all addresses from that area are downloaded
 *   and added to the map, and each address' id is added as a hidden input to the
 *   'create campaign' form.
 *
 *   When an area is deselected, all addresses from that area are removed from the map and form.
 *
 **/
CampaignAddressSelector = new BaseAddressSelector();
CampaignAddressSelector.form = $('#campaign-form'),

/** Get all selected address ids from the form **/
CampaignAddressSelector.selectedIds = function() {
    return $.map(this.form.find('[name="addresses[]"]'), function(input) {
        return input.value;
    });
};

/** Update the form's address ids to those currently selected **/
CampaignAddressSelector.updateForm = function() {
    var form = CampaignAddressSelector.form;
    form.find('[name="addresses[]"]').remove();
    return $.each(Markers.MarkersGetter.markers, function(addr_id) {
        form.append(
            '<input type="hidden" name="addresses[]" value="' + addr_id + '"/>');
    });
};

CampaignAddressSelector.selectArea = function(boundingBox) {
    Markers.MarkersGetter(
        Markers.Marker,
        boundingBox || CampaignAddressSelector.currentBounds(),
        false
    ).done(this.updateForm);
};

CampaignAddressSelector.deselectArea = function(boundingBox) {
    boundingBox = boundingBox || CampaignAddressSelector.currentBounds();
    return this.updateForm(
        $.each(Markers.MarkersGetter.markers, function(addr_id, marker) {
            var address = marker.address;
            if (boundingBox.north > address.lat && boundingBox.south < address.lat &&
                    boundingBox.east > address.lon && boundingBox.west < address.lon){
                Markers.MarkersGetter.remove(addr_id);
            }
        })
    );
};
/** Show the provided addresses (or all selected ones if not provided) on the map **/
CampaignAddressSelector.init = function(address_ids) {
    var params = {
        'addresses[]': address_ids || this.selectedIds(),
        '_xsrf': $('[name="_xsrf"]').val()
    };
    return Markers.MarkersGetter(Markers.Marker, params, true, 'post');
};

window.MarkerHandler = {
    DisplaySelector: DisplaySelector,
    AddressAdder: AddressAdder,
    CampaignAddressSelector: CampaignAddressSelector
}
