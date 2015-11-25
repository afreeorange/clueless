angular.module('Clueless')

.constant('CluelessAPI', 'http://localhost:8000/api')

.config(function($locationProvider, $urlRouterProvider) {
    $locationProvider.html5Mode(true);

    $urlRouterProvider
    .when('', '/')
    .otherwise(
        function($injector, $location) {
            $injector.get('$state').go('404');
        }
    );

})

.config(function (localStorageServiceProvider) {
    localStorageServiceProvider.setPrefix('Clueless');
})

.run(function(localStorageService, BoardService){

    // Get the board ID
    BoardService.getState().then(
        function(response) {
            var loaded_board_id = response.id;
            var cached_board_id = localStorageService.get('board_id');

            if (!cached_board_id) {
                localStorageService.set('board_id', loaded_board_id);
                console.log('Set board ID ' + loaded_board_id);
            } else {
                if (loaded_board_id === cached_board_id) {
                    console.log('Usig existing board ' + cached_board_id);
                } else {
                    localStorageService.clearAll();
                    console.log('Cleared all local storage for new board');
                }
            }
        }, function(response) {
            toastr.error('Could not fetch state for ID');
        });
})

;