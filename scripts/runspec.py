# -*- coding: utf-8 -*-


idColumns = {
	'tabblock': 'blockce10',
	'bg': 'blkgrpce10',
	'tract': 'tractce10',
	'county': 'countyfp10',
}


runs = (
	(
		'tabblock', 'the_geom',
		'tract', 'geom_land_tract_tabblock'
	),
	(
		'bg', 'the_geom',
		'tract', 'geom_land_tract_bg'
	),
	(
		'tabblock', 'the_geom',
		'county', 'geom_land_county_tabblock'
	),
	(
		'bg', 'the_geom',
		'county', 'geom_land_county_bg'
	),
	(
		'tract', 'the_geom',
		'county', 'geom_land_county_tract'
	),
	(
		'tract', 'geom_land_tract_bg',
		'county', 'geom_land_county_tract_bg'
	),
	(
		'tract', 'geom_land_tract_tabblock',
		'county', 'geom_land_county_tract_tabblock'
	),
)
