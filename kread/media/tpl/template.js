/*
 * Haoku Web Project Template
 * Copyright (c) 2014 HaoKu Inc. All Rights Reserved.
 */

 'use strict';

 exports.description = 'Create a Haoku Web Project.'
 exports.notes = ''
 exports.after = ''
 exports.warnOn = '*'

 exports.template = function(grunt, init, done) {

	init.process({type: 'haoku'}, [
		init.prompt('name'),
		init.prompt('title'),
		init.prompt('description', 'This is a HaoKu Web Project.'),
		init.prompt('homepage', 'http://www.haoku.net/'),
		init.prompt('version', '1.0.0'),
		init.prompt('author_name', 'HaoKu Inc.'),
	], function(err, props) {
		var files = init.filesToCopy(props);
		init.copyAndProcess(files, props, {noPorcess: 'libs/**'});
		init.writePackageJSON(props.name + '.json', props);
		init.writePackageJSON('package.json', {
			name: props.name,
			version: props.version,
			devDependencies: {
				"grunt": "~0.4.5",
				"grunt-banner": "~0.2.3",
				"grunt-contrib-clean": "~0.6.0",
				"grunt-contrib-concat": "~0.5.0",
				"grunt-contrib-copy": "~0.5.0",
				"grunt-contrib-csslint": "~0.2.0",
				"grunt-contrib-cssmin": "~0.10.0",
				"grunt-contrib-jshint": "~0.10.0",
				"grunt-contrib-less": "~0.11.3",
				"grunt-contrib-qunit": "~0.5.2",
				"grunt-contrib-uglify": "~0.5.0",
				"grunt-contrib-watch": "~0.6.1",
				"grunt-csscomb": "~3.0.0",
				"grunt-sed": "~0.1.1",
				"load-grunt-tasks": "~0.6.0",
				"markdown": "~0.5.0",
				"time-grunt": "~0.4.0"
			}
		});

		done();
	});
 };
