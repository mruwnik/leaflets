var map = L.map('map-container').setView([50.223262, 19.070912], 16);
L.tileLayer.provider('OpenStreetMap.Mapnik').addTo(map);


/**

   A map marker circle that shows its address when clicked on.

 * @param {Object} address : the address of the point
 *
 **/
Marker = function(address) {
    var colours = {
        color: 'red',
        fillColor: '#f03',
        fillOpacity: 0.5
    };
    this.position = [address.lat, address.lon],
    this.marker = L.circle(this.position, 5, colours)
                   .bindPopup(this.formatAddress(address))
                   .addTo(map);
};
Marker.prototype = {};
Marker.prototype.formatAddress = function(address) {
    return address.street + ' ' + address.house + ',<br>' + address.postcode + ' ' + address.town;
};

/**

   A map marker circle that handles campaign addresses.

   When a CampaignMarker is clicked on, it will toggle its state and notify the database.

 * @param {Object} address : the address of the point
 *
 **/
CampaignMarker = function(address){
    var self = this;
    self.campaignId = CampaignMarker.campaignId()
    self.position = [address.lat, address.lon],
    self.state = address.state == 'marked' ? 'marked' : 'unmarked',
    self.marker = L.circle(this.position, 5, this.currentColour())
                    .on('click', function(e) { self.selected(self.state != 'marked'); })
                    .addTo(map);
    self.address = address;
};
/**
    Get the id of the campaign to which all markers pertain.
 **/
CampaignMarker.campaignId = function() {
    if (!this.campaign_id) {
        this.campaign_id = $('input[name="campaign_id"]').val();
    }
    return this.campaign_id;
};
/**
    All possible marker set ups.
 **/
CampaignMarker.prototype.colours = {
    unmarked: {
        color: 'red',
        fillOpacity: 0.5
    },
    pending: {
        color: 'gray',
        fillOpacity: 0.5
    },
    marked: {
        color: 'blue',
        fillOpacity: 0.5
    }
};
/**
    Return the marker colour for the current state.
 **/
CampaignMarker.prototype.currentColour = function() {
    return this.colours[this.state || 'pending'];
};
/**
    Handle the selection/deselection of a point.
 **/
CampaignMarker.prototype.selected = function(isMarked) {

    // The state is already being updated
    if (this.state == 'pending') {
        return;
    }

    var marker = this.marker,
        self = this;

    marker.setStyle(this.colours.pending);
    marker.state = 'pending';

    var marked = isMarked ? 'marked' : 'unmarked',
        params = {
            campaign: this.campaignId,
            address: this.address.id,
            selected: isMarked,
            '_xsrf': $('[name="_xsrf"]').val()
        };
    return $.post('/campaign/addresses', params, function(result) {
        self.state = marked;
        marker.setStyle(self.currentColour());
    });
}


/**

   Query the given url and create map markers from what is returned.

 * @param {String} url : The url where the markers can be gotten from
 * @param {Object} params : additional parameters to be send
 * @param {Function} markerClass : The marker model (default is Marker)
 **/
fetchMarkers = function(url, params, markerClass) {
    markerClass = markerClass || Marker;
    return $.get(url, params, function(addresses) {
        map.fitBounds($.map(addresses, function(address) {
            var marker = new markerClass(address);
            return [marker.position];
        }));
    });
};


AddressSelector = function(){
    var locationFilter = new L.LocationFilter().addTo(map),
        form = $('#add-campaign-form'),
        addresses = {};

    selectedIds = function() {
        return $.map(form.find('[name="addresses[]"]'), function(input) {
            return input.value;
        });
    },

    updateForm = function(addresses) {
        form.find('[name="addresses[]"]').remove();
        return $.each(addresses, function(addr_id) {
            form.append(
                '<input type="hidden" name="addresses[]" value="' + addr_id + '"/>');
        });
    },

    selectArea = function(boundingBox) {
        fetchMarkers('/addresses/list', boundingBox).done(function(results) {
            addresses = updateForm($.extend(results, addresses));
        });
    },

    deselectArea = function(boundingBox) {
        return updateForm(
            $.each(addresses, function(addr_id, address) {
                if (boundingBox.north > address.lat && boundingBox.south < address.lat &&
                        boundingBox.east > address.lon && boundingBox.west < address.lon){
                    map.removeLayer(address.marker);
                    delete address.marker;
                    delete addresses[addr_id]
                }
            }));
    },

    currentBounds = function() {
        var bounds = locationFilter.getBounds();
        return {
            north: bounds._northEast.lat,
            west: bounds._southWest.lng,
            south: bounds._southWest.lat,
            east: bounds._northEast.lng
        }
    },

    addMarker = function(address) {
        var marker = new Marker(address);
        return [marker.position];
    },

    showAddresses = function(address_ids) {
        var params = {
            'addresses[]': address_ids || selectedIds(),
            '_xsrf': $('[name="_xsrf"]').val()
        };
        return $.post('/addresses/list', params, function(addresses) {
            map.fitBounds($.map(addresses, addMarker));
        });
    },

    addAddresses = function(boundingBox) {
        var boundingBox = boundingBox || currentBounds();
            params = {
                '_xsrf': $('[name="_xsrf"]').val()
            };
        mapErrors.text('searching for addresses...');
        console.log(form);
        console.log(params);
        return $.post('/addresses/search', $.extend(params, boundingBox), function(results) {
            mapErrors.text('');
            $.map(results, addMarker);
            addresses = updateForm($.extend(results, addresses));
        }).error(function(error) {
            mapErrors.text(error.statusText);
        });
    }

    return {
        locationFilter: locationFilter,
        selectedIds: selectedIds,
        updateForm: updateForm,
        selectArea: selectArea,
        deselectArea: deselectArea,
        currentBounds: currentBounds,
        showAddresses: showAddresses,
        addAddresses: addAddresses
    };
}();



var showSelector = $('#show-selector'),
    selectAreaButton = $('#select-area').hide(),
    deselectAreaButton = $('#deselect-area').hide()
    mapButtons = $('.selector-control'),
    mapErrors = $('.map-errors');

showSelector.click(function(){
    mapErrors.text('');
    if(AddressSelector.locationFilter.isEnabled()){
        mapButtons.hide()
        AddressSelector.locationFilter.disable()
    } else {
        mapButtons.show()
        AddressSelector.locationFilter.enable()
    }
    return false;
});

if (window.location.pathname == "/campaign/add") {
    AddressSelector.showAddresses().done(function(addresses) {AddressSelector.addresses = addresses; });

    selectAreaButton.click(function(){
        AddressSelector.selectArea(AddressSelector.currentBounds());
    });

    deselectAreaButton.click(function(){
        AddressSelector.deselectArea(AddressSelector.currentBounds());
    });
} else if (window.location.pathname == "/addresses/import") {
    AddressSelector.form = $('form');
    fetchMarkers(
        '/addresses/list',
        {
            north: 50.226828,
            west: 19.056873,
            south: 50.217513,
            east: 19.084700
        }
    );
    selectAreaButton.click(function(){
        AddressSelector.addAddresses();
    });
} else if (window.location.pathname.lastIndexOf('/campaign', 0) == 0) {
    showSelector.hide();
    fetchMarkers('/campaign/addresses', {campaign: CampaignMarker.campaignId()}, CampaignMarker);
} else {
    showSelector.hide();
    fetchMarkers(
        '/addresses/list',
        {
            north: 50.226828,
            west: 19.056873,
            south: 50.217513,
            east: 19.084700
        }
    );
}
