var map = L.map('map-container').setView([50.223262, 19.070912], 16);
L.tileLayer.provider('OpenStreetMap.Mapnik').addTo(map);


function formatAddress(address) {
    return address.street + ' ' + address.house + ',<br>' + address.postcode + ' ' + address.town;
}


function addressMarker(address) {
    var colours = {
        color: 'red',
        fillColor: '#f03',
        fillOpacity: 0.5
    };
    var position = [address.lat, address.lon],
        marker = L.circle(position, 5, colours)
                   .bindPopup(formatAddress(address))
                   .addTo(map);
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
            'addresses[]': address_ids || AddressSelector.selectedIds(),
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
    },

    findAddresses: function(boundingBox) {
        var boundingBox = boundingBox || AddressSelector.currentBounds();
            params = {
                '_xsrf': AddressSelector.form.find('[name="_xsrf"]').val()
            };
        return $.post('/addresses/search', $.extend(params, boundingBox), function(results) {
            mapErrors.text('');
            AddressSelector.addresses = AddressSelector.updateForm(
                AddressSelector.addMarkers($.extend(results, AddressSelector.addresses)));
        }).error(function(error) {
            mapErrors.text(error.statusText);
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


Campaign = {
    id: $('input[name="campaign_id"]').val(),

    unmarked: {
        color: 'red',
        fillOpacity: 0.5
    },
    pending: {
        color: 'grren',
        fillOpacity: 0.5
    },
    marked: {
        color: 'blue',
        fillOpacity: 0.5
    },
    changeState: function(marker, isMarked) {
        marker.setStyle(Campaign.pending);
        marker.state = 'pending';

        var marked = isMarked ? 'marked' : 'unmarked',
            params = {
                campaign: Campaign.id,
                address: marker.address.id,
                selected: isMarked,
                '_xsrf': $('[name="_xsrf"]').val()
            };
        return $.post('/campaign/addresses', params, function(result) {
            marker.setStyle(Campaign[marked]);
            marker.state = marked;
        });
    },
    toggleSelection: function(event) {
        if(this.state == 'marked') {
            Campaign.changeState(this, false);
        } else if(this.state == 'unmarked') {
            Campaign.changeState(this, true);
        }
    },
    addMarker: function(address) {
        var position = [address.lat, address.lon],
            state = address.state == 'marked' ? 'marked' : 'unmarked',
            marker = L.circle(position, 5, Campaign[state])
                        .on('click', Campaign.toggleSelection)
                        .addTo(map);
            marker.address = address;
            marker.state = state;
        return [position];
    },
    show: function(id) {
        return $.get('/campaign/addresses', {campaign: id || Campaign.id}, function(addresses) {
            map.fitBounds(
                $.map(addresses, function(address, addr_id) {
                    return Campaign.addMarker(address);
                })
            )
        });
    }
};

var showSelector = $('#show-selector'),
    selectAreaButton = $('#select-area').hide(),
    deselectAreaButton = $('#deselect-area').hide()
    mapButtons = $('.selector-control'),
    mapErrors = $('.map-errors');

showSelector.click(function(){
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
    selectAreaButton.click(function(){
        AddressSelector.findAddresses();
    });
} else if (window.location.pathname.lastIndexOf('/campaign', 0) == 0) {
    showSelector.hide();
    Campaign.show();
} else {
    showSelector.hide();
    findAddresses({
        north: 50.226828,
        west: 19.056873,
        south: 50.217513,
        east: 19.084700
    });
}
