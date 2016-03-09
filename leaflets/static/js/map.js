var map = L.map('map-container').setView([50.223262, 19.070912], 16);
L.tileLayer.provider('OpenStreetMap.Mapnik').addTo(map);

function addressMarker(address) {
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
    return marker;
}


function addMarker(address) {
    if (address.marker === undefined) {
        address.marker = addressMarker(address);
        return [[address.lat, address.lon]];
    }
}


var AddressSelector = {
    locationFilter: new L.LocationFilter().addTo(map),

    form: $('#add-campaign-form'),

    selectedIds: function() {
        return $.map(AddressSelector.form.find('[name="addresses[]"]'), function(input) {
            return input.value;
        });
    },

    addresses: {},

    updateForm: function(addresses) {
        AddressSelector.form.find('[name="addresses[]"]').remove();
        return $.each(addresses, function(addr_id) {
            AddressSelector.form.append(
                '<input type="hidden" name="addresses[]" value="' + addr_id + '"/>');
        });
    },

    addMarkers: function (addresses) {
        return $.each(addresses, function(addr_id, address) {
            addMarker(address);
        });
    },

    selectArea: function(boundingBox) {
        $.get('/addresses/list', boundingBox, function(results) {
            AddressSelector.addresses = AddressSelector.updateForm(
                AddressSelector.addMarkers($.extend(results, AddressSelector.addresses)));
        });
    },

    deselectArea: function(boundingBox) {
        return AddressSelector.updateForm(
            $.each(AddressSelector.addresses, function(addr_id, address) {
                if (boundingBox.north > address.lat && boundingBox.south < address.lat &&
                    boundingBox.east > address.lon && boundingBox.west < address.lon){
                    map.removeLayer(address.marker);
                    delete address.marker;
                    delete AddressSelector.addresses[addr_id]
                }
            }));
    },

    currentBounds: function() {
        var bounds = AddressSelector.locationFilter.getBounds();
        return {
            north: bounds._northEast.lat,
            west: bounds._southWest.lng,
            south: bounds._southWest.lat,
            east: bounds._northEast.lng
        }
    },

    showAddresses: function(address_ids) {
        var params = {
            'addresses[]': address_ids === undefined ? AddressSelector.selectedIds() : address_ids,
            '_xsrf': AddressSelector.form.find('[name="_xsrf"]').val()
        };
        return $.post('/addresses/list', params, function(addresses) {
            map.fitBounds(
                $.map(addresses, function(address, addr_id) {
                    addMarker(address);
                    return [[address.lat, address.lon]];
                })
            )
        });
    }
};


function findAddresses (boundingBox) {
    return $.get('/addresses/list', boundingBox, function(addresses) {
        map.fitBounds(
            $.map(addresses, function(address, addr_id) {
                addMarker(address);
                return [[address.lat, address.lon]];
            })
        )
    });
};


if (window.location.pathname == "/campaign/add") {
    AddressSelector.showAddresses().done(function(addresses) {AddressSelector.addresses = addresses; });

    var showSelector = $('#show-selector'),
        selectAreaButton = $('#select-area').hide(),
        deselectAreaButton = $('#deselect-area').hide();

    selectAreaButton.click(function(){
        AddressSelector.selectArea(AddressSelector.currentBounds());
    });

    deselectAreaButton.click(function(){
        AddressSelector.deselectArea(AddressSelector.currentBounds());
    });

    showSelector.click(function(){
        var buttons = $('.selector-control');
        if(AddressSelector.locationFilter.isEnabled()){
            AddressSelector.locationFilter.disable()
            buttons.hide();
        } else {
            AddressSelector.locationFilter.enable()
            buttons.show();
        }
        return false;
    });
} else {
    findAddresses({
        north: 50.226828,
        west: 19.056873,
        south: 50.217513,
        east: 19.084700
    });
}
