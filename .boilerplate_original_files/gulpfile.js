/*
 * Copyright (c) 2013, Divio AG
 * Licensed under BSD
 * http://github.com/aldryn/aldryn-boilerplate-bootstrap3
 */

'use strict';

// #############################################################################
// IMPORTS
var webdriverUpdate;
var argv = require('minimist')(process.argv.slice(2));
var gulp = require('gulp');

// #############################################################################
// SETTINGS
var PROJECT_ROOT = __dirname;
var PROJECT_PATH = {
    bower: PROJECT_ROOT + '/static/vendor',
    css: PROJECT_ROOT + '/static/css',
    docs: PROJECT_ROOT + '/static/docs',
    fonts: PROJECT_ROOT + '/static/fonts',
    html: PROJECT_ROOT + '/templates',
    images: PROJECT_ROOT + '/static/img',
    icons: PROJECT_ROOT + '/private/icons',
    js: PROJECT_ROOT + '/static/js',
    sass: PROJECT_ROOT + '/private/sass',
    tests: PROJECT_ROOT + '/tests'
};

var PROJECT_PATTERNS = {
    images: [
        PROJECT_PATH.images + '/**/*',
        // exclude from preprocessing
        '!' + PROJECT_PATH.images + '/dummy/*/**'
    ],
    js: [
        'gulpfile.js',
        './tools/tasks/**/*.js',
        PROJECT_PATH.js + '/**/*.js',
        PROJECT_PATH.tests + '/**/*.js',
        // exclude from linting
        '!' + PROJECT_PATH.js + '/*.min.js',
        '!' + PROJECT_PATH.js + '/**/*.min.js',
        '!' + PROJECT_PATH.tests + '/coverage/**/*'
    ],
    sass: [
        PROJECT_PATH.sass + '/**/*.{scss,sass}'
    ]
};

var DEFAULT_PORT = 8000;
var PORT = parseInt(process.env.PORT, 10) || DEFAULT_PORT;
var DEBUG = argv.debug;


/**
 * Checks project deployment
 * @param {String} id - task name
 * @returns {Object} - task which finished
 */
function task (id) {
    return require('./tools/tasks/' + id)(gulp, {
        PROJECT_ROOT: PROJECT_ROOT,
        PROJECT_PATH: PROJECT_PATH,
        PROJECT_PATTERNS: PROJECT_PATTERNS,
        DEBUG: DEBUG,
        PORT: PORT
    });
}

gulp.task('bower', task('bower'));
gulp.task('lint:javascript', task('lint/javascript'));
gulp.task('lint', ['lint:javascript']);
gulp.task('sass', task('sass'));
gulp.task('build', ['sass']);

/**
 * GULP_MODE === 'production' means we have a limited
 * subset of tasks, namely sass, bower and lint to
 * speed up the deployment / installation process.
 */
if (process.env.GULP_MODE !== 'production') {
    gulp.task('images', task('images'));
    gulp.task('docs', task('docs'));
    gulp.task('preprocess', ['sass', 'images', 'docs']);
    gulp.task('icons', task('icons'));

    gulp.task('browser', task('browser'));

    gulp.task('tests:lint', ['lint:javascript']);
    gulp.task('tests:unit', task('tests/unit'));
    gulp.task('tests:watch', ['tests:lint'], task('tests/watch'));
    gulp.task('tests', ['tests:unit', 'tests:integration', 'tests:lint']);

    webdriverUpdate = require('gulp-protractor').webdriver_update;
    gulp.task('tests:webdriver', webdriverUpdate);
    gulp.task('tests:integration', ['tests:webdriver'], task('tests/integration'));
}

gulp.task('watch', function () {
    gulp.watch(PROJECT_PATTERNS.sass, ['sass']);
    gulp.watch(PROJECT_PATTERNS.js, ['lint']);
});

gulp.task('default', ['bower', 'sass', 'lint', 'watch']);
