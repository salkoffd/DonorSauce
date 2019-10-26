// Create legislator map

function createMap(senatorLayer, representativeLayer) {
    // Create the tile layer that will be the background of our map
    var lightmap = L.tileLayer("https://api.tiles.mapbox.com/v4/{id}/{z}/{x}/{y}.png?access_token={accessToken}", {
        attribution: "Map data &copy; <a href=\"https://www.openstreetmap.org/\">OpenStreetMap</a> contributors, <a href=\"https://creativecommons.org/licenses/by-sa/2.0/\">CC-BY-SA</a>, Imagery © <a href=\"https://www.mapbox.com/\">Mapbox</a>",
        maxZoom: 18,
        id: "mapbox.light",
        accessToken: API_KEY
    });

    // Create a baseMaps object to hold the lightmap layer
    var baseMaps = {
        "Light Map": lightmap
    };

    // Create an overlayMaps object to hold the legislators layer
    var overlayMaps = {
        "Senators": senatorLayer,
        "Representatives": representativeLayer
    };

    // Create the map object with options
    var myMap = L.map("map", {
        center: [38, -97], // var newYorkCoords = [40.73, -74.0059];
        zoom: 5,
        layers: [lightmap, senatorLayer, representativeLayer]
    });

    // Create a layer control, pass in the baseMaps and overlayMaps. Add the layer control to the map
    L.control.layers(baseMaps, overlayMaps, {
        collapsed: false
    }).addTo(myMap);

};

function createMarkers(response) {
    console.log(Math.random())
    // Custom markers
    var redIcon = new L.Icon({
        iconUrl: 'https://cdn.rawgit.com/pointhi/leaflet-color-markers/master/img/marker-icon-red.png',
        shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
        iconSize: [25, 41],
        iconAnchor: [12, 41],
        popupAnchor: [1, -34],
        shadowSize: [41, 41]
    });
    var blueIcon = new L.Icon({
        iconUrl: 'https://cdn.rawgit.com/pointhi/leaflet-color-markers/master/img/marker-icon-blue.png',
        shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
        iconSize: [25, 41],
        iconAnchor: [12, 41],
        popupAnchor: [1, -34],
        shadowSize: [41, 41]
    });
    var greyIcon = new L.Icon({
        iconUrl: 'https://cdn.rawgit.com/pointhi/leaflet-color-markers/master/img/marker-icon-grey.png',
        shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
        iconSize: [25, 41],
        iconAnchor: [12, 41],
        popupAnchor: [1, -34],
        shadowSize: [41, 41]
    });

    // Initialize an array to hold representative and senator markers
    var senatorMarkers = [];
    var representativeMarkers = [];

    // Loop through the legislator object
    var nLegislators = Object.keys(response).length;
    for (i = 0; i < nLegislators; i++) {

        // For each person, create a marker and bind a popup with info
        if (response[i].latitude) {
            // Democrat or Republican or Independent?
            if (response[i].party == 'Democrat') {
                var myIcon = blueIcon;
            }
            else if (response[i].party == 'Republican') {
                var myIcon = redIcon;
            }
            else {
                var myIcon = greyIcon;
            };
            // Senator or Representative?
            if (response[i].leg_type == 'sen') {
                var leg_type = 'Senator'
            }
            else {
                var leg_type = "Representative"
            }
            // create list of top donors
            var donorHTML = [];
            for (ii = 0; ii < 5; ii++) {
                thisDonorInfo = response[i].top_donors[ii] + ", " + response[i].top_donors_amounts[ii]
                donorHTML = donorHTML + ("<p>" + thisDonorInfo + "</p>")
            }
            // create marker
            // jiggle the location a bit so senator markers aren't on top of eachother
            var jiggle = Math.random() / 10;
            var myMarker = L.marker([response[i].latitude, response[i].longitude + jiggle], { icon: myIcon })
                .bindPopup('<div class="popup">' +
                    "<h3>" + response[i].first_name + " " + response[i].last_name + "</h3><hr>" +
                    "<p>" + leg_type + ", " + response[i].state + "</p>" +
                    '<a href="' + response[i].url + '">' + response[i].url + '</a>' +
                    // add donor info
                    donorHTML +
                    "</div>"
                );
        }
        else {
            console.log(response[i].first_name + " " + response[i].last_name + " omitted")
        };

        // Add the marker to the senator or rep array
        if (response[i].leg_type == 'sen') {
            senatorMarkers.push(myMarker);
        }
        else {
            representativeMarkers.push(myMarker);
        };

        // Create a layer group made from the markers array, pass it into the createMap function
        var senatorLayer = L.layerGroup(senatorMarkers);
        var representativeLayer = L.layerGroup(representativeMarkers);
    };

    createMap(senatorLayer, representativeLayer);
};

// GeoJSON url
var url = "api/legislators";
// get legislator data
d3.json(url, function (response) {
    // create markers with function
    createMarkers(response)
});