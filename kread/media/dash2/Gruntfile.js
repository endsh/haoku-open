'use strict';

module.exports = function(grunt) {

	grunt.initConfig({
		pkg: grunt.file.readJSON('dash.json'),
		banner: '/*\n * <%= pkg.name %> - v<%= pkg.version %> - ' +
			'<%= grunt.template.today("yyyy-mm-dd") %>\n' +
			'<%= pkg.homepage ? " * home: " + pkg.homepage + "\\n" : "" %>' +
			' * Copyright (c) <%= grunt.template.today("yyyy") %> <%= pkg.author.name %>' +
			' All Rights Reserved.\n */\n',

		clean: {
			files: ['dist']
		},

		concat: {
			options: {
				banner: '<%= banner %>',
			},
			dist: {
				src: [
					'src/js/account.js',
					'src/js/check.js',
					'src/js/dash.js',
					'src/js/message.js',
				],
				dest: 'dist/js/<%= pkg.name %>.js'
			}
		},

		uglify: {
			options: {
				banner: '<%= banner %>'
			},
			dist: {
				src: [
					'libs/jquery-1.11.1.min.js', 
					'libs/bootstrap/js/bootstrap.min.js',
					'<%= concat.dist.dest %>',
				],
				dest: 'dist/js/<%= pkg.name %>.min.js'
			}
		},

		jshint: {
			options: {
				jshintrc: 'src/js/.jshintrc'
			},
			gruntfile: {
				options: {
					jshintrc: 'grunt/.jshintrc'
				},
				src: 'Gruntfile.js'
			},
			js: {
				src: ['src/js/*.js']
			},
		},

		less: {
			options: {
				banner: '<%= banner %>'
			},
			dist: {
				files: {
					'dist/css/<%= pkg.name %>.css': 'src/less/dash.less'
				}
			}
		},

		cssmin: {
			options: {
				banner: '<%= banner %>',
			},
			dist: {
				files: {
					'dist/css/<%= pkg.name %>.min.css': [
						'libs/bootstrap/css/bootstrap.min.css',
						'dist/css/<%= pkg.name %>.css'
					]
				}
			}
		},

		csslint: {
			options: {
				csslintrc: 'src/less/.csslintrc'
			},
			css: 'dist/css/dash.css'
		},

		watch: {
			gruntfile: {
				files: '<%= jshint.gruntfile.src %>',
				tasks: ['jshint:gruntfile'],
			},
			js: {
				files: '<%= jshint.js.src %>',
				tasks: ['jshint:js', 'concat']
			},
			css: {
				files: 'src/less/*.less',
				tasks: ['less', 'csslint']
			}
		},

		copy: {
			fonts: {
				expand: true,
				cwd: 'libs/bootstrap',
				src: 'fonts/*',
				dest: 'dist/',
			},
			src: {
				expand: true,
				cwd: 'src',
				src: ['img/*', 'robots.txt'],
				dest: 'dist/',
			}
		}
	});

	require('load-grunt-tasks')(grunt);
	require('time-grunt')(grunt);

	grunt.registerTask('dist-css', ['less', 'cssmin']);
	grunt.registerTask('dist-js', ['concat', 'uglify']);
	grunt.registerTask('dist-copy', ['copy']);
	grunt.registerTask('all', ['clean', 'dist-css', 'dist-js', 'dist-copy']);
	grunt.registerTask('default', ['less', 'concat']);
};