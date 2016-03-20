var map = L.map('map-container').setView([50.223262, 19.070912], 16);
L.tileLayer.provider('OpenStreetMap.Mapnik').addTo(map);
var markersLayer = L.markerClusterGroup({
    showCoverageOnHover: false,
    removeOutsideVisibleBounds: true,
    disableClusteringAtZoom: 19,
    iconCreateFunction: function(cluster) {
       var childCount = cluster.getChildCount();

        var selected = cluster.getAllChildMarkers().reduce(function(prev, curr) {
            return prev + (curr.state == 'marked' ? 1 : 0);
        }, 0);

        var c = ' marker-cluster-';
        if (childCount == selected) {
            c += 'all-selected';
        } else if (selected > 0) {
            c += 'some-selected';
        } else {
            c += 'none-selected';
        }

        return new L.DivIcon({
            html: '<div><span>' + childCount + '</span></div>',
            className: 'marker-cluster' + c,
            iconSize: new L.Point(40, 40)
        });
    }
}).addTo(map);


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
    this.address = address;
    this.position = [address.lat, address.lon];
    this.marker = L.circle(this.position, 5, colours)
                   .bindPopup(this.formatAddress(address));
};
Marker.prototype = {};
Marker.prototype.formatAddress = function(address) {
    return address.street + ' ' + address.house + ',<br>' + address.postcode + ' ' + address.town;
};
Marker.defaultBounds = {
    north: 50.226828,
    west: 19.056873,
    south: 50.217513,
    east: 19.084700
}
Marker.url = '/addresses/list';


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
    self.address = address;
    self.marker = L.circleMarker(this.position, this.currentColour())
                    .on('click', function(e) { self.selected(self.marker.state != 'marked'); });
    self.marker.state = address.state;
};

CampaignMarker.prototype = {};

/**
    Get the id of the campaign to which all markers pertain.
 **/
CampaignMarker.campaignId = function() {
    if (!this.campaign_id) {
        this.campaign_id = $('input[name="campaign_id"]').val();
    }
    return this.campaign_id;
};
CampaignMarker.defaultBounds = {campaign: CampaignMarker.campaignId()};
CampaignMarker.url = '/campaign/addresses';
/**
    All possible marker set ups.
 **/
CampaignMarker.prototype.colours = {
    selected: {
        color: 'red',
        fillOpacity: 0.5,
        radius: 15
    },
    pending: {
        color: 'gray',
        fillOpacity: 0.5,
        radius: 15
    },
    marked: {
        color: 'blue',
        fillOpacity: 0.5,
        radius: 15
    }
};
/**
    Return the marker colour for the current state.
 **/
CampaignMarker.prototype.currentColour = function() {
    var marker = this.marker || this.address;
    return this.colours[marker.state || 'pending'];
};
CampaignMarker.prototype.initSocket = function() {

    // If the socket is already initialised and working, just return
    if (CampaignMarker.prototype.socket && CampaignMarker.prototype.socket.readyState <= 1) {
        return CampaignMarker.prototype.socket;
    }

    var socket = new WebSocket('ws://127.0.0.1:5000/campaign/mark')

    socket.onmessage = function (event) {
        var address = JSON.parse(event.data),
            point = MarkersGetter.markers[address.id],
            marker = point.marker;
        marker.state = address.state;
        marker.setStyle(point.currentColour());
        markersLayer.refreshClusters([marker]);
    };

    CampaignMarker.prototype.socket = socket;
    return socket;
};

CampaignMarker.prototype.initSocket();

/**
    Send a message to the websocket.

    If the socket has been disconnected, reconnect and resend the message.
 **/
CampaignMarker.prototype.sendMessage = function(message) {
    if (this.socket.readyState > 1) {
        this.initSocket();
    }

    try {
        this.socket.send(message);
    } catch (err) {
        this.initSocket();
        var self = this,
            // Pretend to asynchronisly wait for the connection to be available.
            repeater = setTimeout(function(){
                if (self.socket.readyState < 1) { // 0 means that the connection is being initialised
                    return;
                } else if (self.socket.readyState == 1) { // 1 means that the connection is receiving messages
                    self.socket.send(message);
                }
                clearTimeout(repeater); // any value other than 0 should cause the function to finish
            }, 100);
    }
}
/**
    Handle the selection/deselection of a point.
 **/
CampaignMarker.prototype.selected = function(isMarked) {
    // The state is already being updated
    if (this.marker.state == 'pending') {
        return;
    }

    this.marker.setStyle(this.colours.pending);
    this.marker.state = 'pending';

    this.sendMessage(JSON.stringify({
        campaign: this.campaignId,
        address: this.address.id,
        state: isMarked ? 'marked' : 'selected'
    }));
}


/**

   Query the given url and create map markers from what is returned.

 * @param {Function} markerClass : The marker model (default is Marker)
 * @param {String} url : The url where the markers can be gotten from
 * @param {Object} params : additional parameters to be send

 **/
MarkersGetter = function(markerClass, params, fitResults, method) {
    markerClass = markerClass || Marker;
    params = params || markerClass.defaultBounds;
    fitResults = fitResults === undefined ? true : fitResults;
    method = method || 'get';
    method = method.toLowerCase() == 'post' ? $.post : $.get;

    return method(markerClass.url, params, function(addresses) {
        var markers = [],
            points = $.map(addresses, function(address) {
                if (MarkersGetter.markers[address.id] === undefined) {
                    var marker = new markerClass(address);
                    MarkersGetter.markers[marker.address.id] = marker;
                    markers.push(marker.marker);
                }
                return [marker.position];
            });
        markersLayer.addLayers(markers);
        if (fitResults) {
            map.fitBounds(points);
        }
    });
};
MarkersGetter.markers = {};
/**
    Remove the given addresses marker from the map.
 **/
MarkersGetter.remove = function(addressId) {
    var marker = this.markers[addressId];
    map.removeLayer(marker.marker);
    delete marker.marker;
    delete this.markers[addressId];
};


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
    return new Marker(address);
};
BaseAddressSelector.prototype.init = function() {
    MarkersGetter(mapControls.markerClass);
};
BaseAddressSelector.prototype.selectArea = function() {};
BaseAddressSelector.prototype.deselectArea = function() {};


/** A simple selector that only displays addresses **/
DisplaySelector = new BaseAddressSelector();


/**
    Handle adding new addresses to the system.
 **/
AddressAdder = new BaseAddressSelector();
AddressAdder.selectArea = function(boundingBox) {
    var boundingBox = boundingBox || this.currentBounds();
        params = {
            '_xsrf': this.xsrf
        };
    mapControls.errors.text('searching for addresses...');
    return $.post('/addresses/search', $.extend(params, boundingBox), function(results) {
        mapControls.errors.text('');
        AddressAdder.markers = $.extend($.map(results, AddressAdder.newMarker), AddressAdder.markers);
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
CampaignAddressSelector.form = $('#add-campaign-form'),

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
    return $.each(MarkersGetter.markers, function(addr_id) {
        form.append(
            '<input type="hidden" name="addresses[]" value="' + addr_id + '"/>');
    });
};

CampaignAddressSelector.selectArea = function(boundingBox) {
    MarkersGetter(Marker, boundingBox || CampaignAddressSelector.currentBounds(), false).done(this.updateForm);
};

CampaignAddressSelector.deselectArea = function(boundingBox) {
    boundingBox = boundingBox || CampaignAddressSelector.currentBounds();
    return this.updateForm(
        $.each(MarkersGetter.markers, function(addr_id, marker) {
            var address = marker.address;
            if (boundingBox.north > address.lat && boundingBox.south < address.lat &&
                    boundingBox.east > address.lon && boundingBox.west < address.lon){
                MarkersGetter.remove(addr_id);
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
    return MarkersGetter(Marker, params, true, 'post');
};



/**
    Work out what the current configuration is
 **/
var markerClasses = {
    'Marker': Marker,
    'CampaignMarker': CampaignMarker,
}
var handlerClasses = {
    'DisplaySelector': DisplaySelector,
    'AddressAdder': AddressAdder,
    'CampaignAddressSelector': CampaignAddressSelector
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
        mapControls.mapButtons.show()
        mapControls.addressHandler.locationFilter.enable()
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
