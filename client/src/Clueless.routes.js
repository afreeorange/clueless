angular.module('Clueless')

.config(function($stateProvider) {

    $stateProvider

    .state('index', {
        url: '/',
        views: {
            '@': {
                controller: 'gameController',
                controllerAs: 'gc',
                resolve: {
                    gameState: function(GameService) {
                        return GameService.getState();
                    }
                }
            },

            'logs@index': {
                templateUrl: 'CluelessLogs.html',
                controller: 'logsController',
                controllerAs: 'lc',
                resolve: {
                    logs: function(LogsService) {
                        return LogsService.getLogs();
                    }
                }
            }
        }
    })

    .state('404', {
        url: '/oops',
        views: {
            '@': {
                template: 'What\'t <em>that</em>?'
            }
        }
    })

    ;
    
});
        
