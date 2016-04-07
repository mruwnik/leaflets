/**
    Marker definitions.

    A marker is simply a point on the map. Various markers can add extra functionality.
    The following markers are defined:

     * Marker - the default marker that just shows the address when clicked on

     * CampaignMarker - toggles whether the given address has been selected or not when
            clicked on. This is done via websockets (when available), so any
            change will immediately be automatically updated for to all users.
            The following colours can be displayed by this marker:
        - red   - the given address has not been visited
        - blue  - the given address has been visited
        - grey  - the given address is being updated
**/



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
    north: 54.226828,
    west: 1.056873,
    south: 40.217513,
    east: 109.084700
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

    var socket = new WebSocket(window.location.origin.replace('http', 'ws') + '/campaign/mark');

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

/**
    Send a message to the websocket.

    If the socket has been disconnected, reconnect and resend the message.
 **/
CampaignMarker.prototype.sendMessage = function(message) {
    message = JSON.stringify(message);
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
    Handle the selection/deselection of a point via normal POST.
 **/
CampaignMarker.prototype.postMessage = function(params) {
    params['_xsrf'] = $('[name="_xsrf"]').val();
    return $.post('/campaign/addresses', params, function(result) {
        var point = MarkersGetter.markers[params.address],
            marker = point.marker;
        marker.state = params.state;
        marker.setStyle(point.currentColour());
        markersLayer.refreshClusters([marker]);
    });
}

try {
    CampaignMarker.prototype.initSocket();
    CampaignMarker.prototype.updater = CampaignMarker.prototype.sendMessage;
} catch(err) {
    CampaignMarker.prototype.updater = CampaignMarker.prototype.postMessage;
}

/**
    Handle the selection/deselection of a point via websockets.
 **/
CampaignMarker.prototype.selected = function(isMarked) {
    // The state is already being updated
    if (this.marker.state == 'pending') {
        return;
    }

    this.marker.setStyle(this.colours.pending);
    this.marker.state = 'pending';

    this.updater({
        campaign: this.campaignId,
        address: this.address.id,
        state: isMarked ? 'marked' : 'selected'
    });
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
                var marker = MarkersGetter.markers[address.id];
                if (marker === undefined) {
                    marker = new markerClass(address);
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


window.Markers = {
    Marker: Marker,
    CampaignMarker: CampaignMarker,
    MarkersGetter: MarkersGetter
}
