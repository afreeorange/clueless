angular.module('Clueless')

.config(function($stateProvider) {

    $stateProvider
    .state('index', {
        url: '/',
        views: {
            '@': {
                template: 'Welcome!'
            },
            'board@': {
                templateUrl: 'CluelessBoard.html',
                controller: 'boardController',
                controllerAs: 'bc',
                resolve: {
                    boardState: function(BoardService) {
                        return BoardService.getState();
                    },
                    boardMetadata: function(BoardService) {
                        return BoardService.getMetadata();
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
                template: 'HELLOWWWWWWW'
            }
        }
    })
    ;
    
});
        
