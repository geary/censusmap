// polytest.js
// By Michael Geary - http://mg.to/
// See UNLICENSE or http://unlicense.org/ for public domain notice.

$().ready( function() {
	// The RNG argument is a random seed, not a magic number
	var rng = new RNG( 0.5526181932073087 )
	
	var gm = google.maps, gme = gm.event;
	var $mapdiv = $('#map'), mapdiv = $mapdiv[0], map;
	map = new gm.Map( mapdiv, {
		mapTypeId: google.maps.MapTypeId.ROADMAP
	});
	
	//map.fitBounds( new gm.LatLngBounds(
	//	new gm.LatLng( 18.9483, -159.7644 ),
	//	new gm.LatLng( 22.2290, -154.8078 )
	//) );
	//map.fitBounds( new gm.LatLngBounds(
	//	new gm.LatLng( 21.254742, -158.282089 ),
	//	new gm.LatLng( 21.715012, -157.648444 )
	//) );
	
	var file = location.search.slice(1) || 'geotest.json';
	$.getJSON( file, function( geo ) {
		if( geo.type != 'FeatureCollection' ) return;
		geo.features.forEach( function( feature ) {
			feature.fillColor = '#' + rng.nextFloat().toString(16).slice(2,8);
			feature.fillOpacity = rng.nextFloat() * .5 + .1;
			feature.strokeColor = '#000000';
			feature.strokeOpacity = 0.2;
			feature.strokeWidth = 1;
		});
		
		var goog =
			geo.crs  &&
			geo.crs.type == 'name'  &&
			/:3857$|:900913$/.test( geo.crs.properties.name );
		
		function zoomToBbox( bbox ) {
			function toLat( m ) { return goog ? metersToLat(m) : m; }
			function toLng( m ) { return goog ? metersToLng(m) : m; }
			
			var
				sw = new gm.LatLng( toLat(bbox[1]), toLng(bbox[0] ) ),
				ne = new gm.LatLng( toLat(bbox[3]), toLng(bbox[2] ) ),
				bounds = new gm.LatLngBounds( sw, ne );
			map.fitBounds( bounds );
		}
		
		zoomToBbox( geo.bbox );
		
		var overFeature;
		var $where = $('#where');
		
		var gonzo = new PolyGonzo.PgOverlay({
			map: map,
			geo: geo,
			events: {
				mousemove: function( event, where ) {
					var feature = where && where.feature;
					// TODO: add mouseenter/leave to PG and
					// use instead of mousemove/overFeature
					if( feature != overFeature ) {
						overFeature = feature;
						$where.html( feature.properties.name );
					}
				},
				click: function( event, where ) {
					var feature = where && where.feature;
					feature && zoomToBbox( feature.bbox );
				}
			}
		});
		gonzo.setMap( map );
	});
});


function latToMeters( lat ) {
	return(
		Math.log( Math.tan( ( 90 + lat ) * Math.PI / 360 ) ) /
		( Math.PI / 180 ) *
		20037508.34 / 180
	);
}

function lngToMeters( lng ) {
	return lng * 20037508.34 / 180;
}

function metersToLat( y ) {
	return(
		180 / Math.PI *
		(
			Math.atan(
				Math.exp( ( y / 20037508.34 * 180 ) * Math.PI / 180 )
			) * 2 -
			Math.PI / 2
		)
	);
}

function metersToLng( x ) {
	return x / 20037508.34 * 180;
}
