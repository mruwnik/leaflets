window.map = L.map('map-container').setView([50.223262, 19.070912], 16);
L.tileLayer.provider('OpenStreetMap.Mapnik').addTo(map);
window.markersLayer = L.markerClusterGroup({
    showCoverageOnHover: true,
    removeOutsideVisibleBounds: true,
    disableClusteringAtZoom: $('#map-container').data('clustering-zoom'),
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

        // If there are some addresses selected, and it will fit in the cluster circle, show how many are selected
        var contents = childCount;
        if (selected > 0 && selected < childCount && (selected + ' / ' + childCount).length < 7) {
            contents = selected + ' / ' + childCount;
        }

        return new L.DivIcon({
            html: '<div><span>' + contents + '</span></div>',
            className: 'marker-cluster' + c,
            iconSize: new L.Point(40, 40)
        });
    }
}).addTo(map);
