angular.module('Clueless')

.constant('CluelessAPI', 'http://localhost:8000/api')

.constant('CluelessSocketServer', 'http://localhost:8000')

.config(function($locationProvider, $urlRouterProvider) {
    $locationProvider.html5Mode(true);

    // Set default route
    $urlRouterProvider
        .when('', '/')
        .otherwise(
            function($injector, $location) {
                $injector.get('$state').go('404');
            }
        );

})

.config(function(localStorageServiceProvider) {
    localStorageServiceProvider.setPrefix('Clueless');
})

.run(function(localStorageService, GameService, SocketService, $http) {

    // Manage local storage based on Board ID
    GameService.getState().then(

        function(response) {
            var loaded_board_id = response.id;
            var cached_board_id = localStorageService.get('board_id');
            var player_token = localStorageService.get('player_token');

            if (loaded_board_id === cached_board_id) {
                console.log('Using existing board ' + cached_board_id);

                if (player_token) {
                    console.log('Fetching data for existing player token');
                    SocketService.emit('board:playerdata', {
                        'token': player_token
                    });
                }

            } else {
                localStorageService.clearAll();
                console.log('Cleared all local storage for new board');

                localStorageService.set('board_id', loaded_board_id);
                console.log('Set board ID ' + loaded_board_id);
            }
        },

        function(response) {
            toastr.error('Could not fetch state for ID');
        });

})

;

// Global settings for all toast notifications
toastr.options = {
    "closeButton": false,
    "debug": false,
    "newestOnTop": false,
    "progressBar": true,
    "positionClass": "toast-bottom-left",
    "preventDuplicates": false,
    "showDuration": "600",
    "hideDuration": "1000",
    "timeOut": "5000",
    "extendedTimeOut": "1000",
    "showEasing": "swing",
    "hideEasing": "linear",
    "showMethod": "fadeIn",
    "hideMethod": "fadeOut"
};