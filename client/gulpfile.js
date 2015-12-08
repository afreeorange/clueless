var gulp = require('gulp'),
    addStream = require('add-stream'),
    $ = require('gulp-load-plugins')({pattern: ['gulp-*', 'gulp.*'], camelize: true}),
    del = require('del')
    ;

var development_host = '127.0.0.1';
var development_port = 5000;

var paths = {
    vendor: {
        styles: [
            'bower_components/flexboxgrid/dist/flexboxgrid.min.css',
            'bower_components/font-awesome/css/font-awesome.min.css',
            'bower_components/toastr/toastr.min.css'
        ],
        scripts: [
            'bower_components/jquery/dist/jquery.min.js',
            'bower_components/toastr/toastr.min.js',
            'bower_components/moment/min/moment.min.js',
            'bower_components/loglevel/dist/loglevel.min.js',
            'static/js/*.js',
            'bower_components/angular/angular.min.js',
            'bower_components/angular-ui-router/release/angular-ui-router.min.js',
            'bower_components/angular-local-storage/dist/angular-local-storage.min.js',
            'bower_components/angular-moment/angular-moment.min.js',
            'bower_components/angular-moment/angular-poller.min.js',
            'bower_components/angular-socket-io/socket.min.js'
        ]
    },
    app: {
        styles: [
            'src/**/*.less'
        ],
        scripts: [
            'src/**/Clueless.module.js',
            'src/**/*config.js',
            'src/**/*filters.js',
            'src/**/*directives.js',
            'src/**/*services.js',
            'src/**/*controller*.js',
            'src/**/*routes*.js'
        ],
        templates: [
            'src/**/*.jade'
        ],
        images: [
          '!static/img/src',
          '!static/img/src/*',
          'static/img/**'
        ],
        fonts: [
          'bower_components/font-awesome/fonts/**'
        ]
    },
    source: 'src',
    destination: 'dist'
}

// ------ Images ------

gulp.task('images', [], function() {
    return gulp.src(paths.app.images)
               .pipe(gulp.dest(paths.destination + '/images'));
});

// ------ Fonts ------

gulp.task('fonts', [], function() {
    return gulp.src(paths.app.fonts)
               .pipe(gulp.dest(paths.destination + '/fonts'));
});

// ------ Scripts ------    

function prepareTemplatesForCaching() {
    return gulp.src(paths.app.templates)
               .pipe($.debug())
               .pipe($.jade())
               .pipe($.angularTemplatecache({module: 'Clueless'}));
}

gulp.task('vendor.scripts', [], function() {
    return gulp.src(paths.vendor.scripts)
               .pipe($.debug())
               .pipe($.uglify())
               .pipe($.concat('vendor.js'))
               .pipe(gulp.dest(paths.destination + '/scripts'));
});

gulp.task('app.scripts', [], function() {
    return gulp.src(paths.app.scripts)
               .pipe($.debug())
               .pipe($.jshint())
               .pipe($.jshint.reporter('jshint-stylish'))
               .pipe($.ngAnnotate({single_quotes: true}))
               // .pipe($.uglify())
               .pipe(addStream.obj(prepareTemplatesForCaching()))
               .pipe($.concat('app.js'))
               .pipe(gulp.dest(paths.destination + '/scripts'));
});

gulp.task('scripts', ['vendor.scripts', 'app.scripts'], function() {
    return;
});

// ------ Styles ------

gulp.task('vendor.styles', [], function() {
    return gulp.src(paths.vendor.styles)
               .pipe($.debug())
               .pipe($.cssmin())
               .pipe($.concat('vendor.css'))
               .pipe(gulp.dest(paths.destination + '/styles'));
});

gulp.task('app.styles', [], function() {
    return gulp.src(paths.app.styles)
               .pipe($.debug())
               .pipe($.concat('app.less'))
               .pipe($.less())
               .pipe($.recess({noIDs: false, strictPropertyOrder: false, noOverqualifying: false})) // Because it's 2AM and I don't care.
               .pipe($.recess.reporter())
               .pipe($.autoprefixer())
               .pipe($.cssmin())
               .pipe($.rename('app.css'))
               .pipe(gulp.dest(paths.destination + '/styles'));
});

gulp.task('styles', ['vendor.styles', 'app.styles'], function() {
    return;
});

// ------ Templates ------

gulp.task('templates', [], function() {
    return gulp.src(paths.source + '/Clueless.jade')
               .pipe($.debug())
               .pipe($.jade())
               .pipe($.rename('index.html'))
               .pipe(gulp.dest(paths.destination));
});

// ------ Other tasks ------

gulp.task('watch', ['app.styles', 'app.scripts', 'templates'], function() {
    gulp.watch(paths.app.styles, ['app.styles']);
    gulp.watch(paths.app.scripts, ['app.scripts']);
    gulp.watch(paths.app.templates, ['app.scripts', 'templates']);
});

gulp.task('clean', [], function() {
    del(paths.destination);
});

gulp.task('serve', [], function() {
    gulp.src(paths.destination)
    .pipe($.webserver({
        host: development_host,
        port: development_port,
        livereload: true,
        directoryListing: false,
        fallback: 'index.html',
        open: false
    }));
});

// ------ Main task ------

gulp.task('default', ['clean', 'images', 'fonts', 'styles', 'scripts', 'templates'], function() {
    return;
});
