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
                    },
                    gameMetadata: function(GameService) {
                        return GameService.getMetadata();
                    }
                }
            },

            'logs@': {
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
    
});
        
