'use strict';

module.exports = function(grunt) {

	grunt.initConfig({
		pkg: grunt.file.readJSON('accounts.json'),
		banner: '/*\n * <%= pkg.name %> - v<%= pkg.version %> - ' +
			'<%= grunt.template.today("yyyy-mm-dd") %>\n' +
			'<%= pkg.homepage ? " * home: " + pkg.homepage + "\\n" : "" %>' +
			' * Copyright (c) <%= grunt.template.today("yyyy") %> <%= pkg.author.name %>' +
			' All Rights Reserved.\n */\n',

		clean: {
			files: [
				'dist/js/*.js',
				'dist/css/*.css',
			]
		},

		concat: {
			options: {
				banner: '<%= banner %>',
			},
			dist: {
				src: [
					'src/js/accounts.js',
					'src/js/contant.js',
					'src/js/message.js',
					'src/js/check.js',
					'src/js/register.js',
					'src/js/login.js',
					'src/js/logout.js',
					'src/js/profile.js',
					'src/js/reset.js',
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
					'libs/jquery.form.js', 
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
					'dist/css/<%= pkg.name %>.css': 'src/less/accounts.less'
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

		watch: {
			gruntfile: {
				files: '<%= jshint.gruntfile.src %>',
				tasks: ['jshint:gruntfile'],
			},
			js: {
				files: '<%= jshint.js.src %>',
				tasks: ['concat', 'jshint:js']
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
			img: {
				expand: true,
				src: 'img/*', 
				dest:'dist/',
			},
			src: {
				expand: true,
				cwd: 'src',
				src: ['robots.txt'],
				dest: 'dist/',
			}
		}
	});

	require('load-grunt-tasks')(grunt);
	require('time-grunt')(grunt);

	grunt.registerTask('dist-css', ['less', 'cssmin']);
	grunt.registerTask('dist-js', ['concat', 'uglify']);
	grunt.registerTask('dist-copy', ['copy']);
	grunt.registerTask('build', ['clean', 'dist-css', 'dist-js', 'dist-copy']);
	grunt.registerTask('default', ['build']);
};