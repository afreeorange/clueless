angular.module('Clueless')

.factory('BoardService', function(CluelessAPI, $http, localStorageService) {
    var service = {};

    service.metadata = $http.get(CluelessAPI + '/meta');

    service.getMetadata = function() {
        return service.metadata;
    };

    service.getState = function() {
        return $http.get(CluelessAPI)
            .then(
                function(response) {
                    console.log('Fetched board state.');
                    return response.data;
                },
               function(response) {
                    toastr.error('Could not get board state');
                }
            );
    };

    service.addedPlayer = function() {
        return localStorageService.get('player_token') ? true : false;
    };

    service.addPlayer = function(playerName, suspect) {
        data = {
            'name': playerName,
            'suspect': suspect
        };

        return $http.post(CluelessAPI + '/players', data)
            .then(
                function(response) {
                    toastr.success('Created new player');
                    console.log('Player token is ' + response.data.player_token);
                    localStorageService.set('player_token', response.data.player_token);
                    return response.data;
                },
               function(response) {
                    toastr.error(response.data.error);
                }
            );
    };

    service.movePlayer = function(space) {
        data = {
            'token': localStorageService.get('player_token'),
            'space': space
        };

        return $http.put(CluelessAPI + '/move', data)
            .then(
                function(response) {
                    toastr.success('Moved player');
                    return response.data;
                },
               function(response) {
                    toastr.error(response.data.message);
                }
            );
    };

    service.makeSuggestion = function() {};

    return service;
})

.factory('LogsService', function(CluelessAPI, $http) {
    var service = {};

    service.getLogs = function() {
        return $http.get(CluelessAPI + '/logs')
            .then(
                function(response) {
                    return response.data;
                },
               function(response) {
                    toastr.error('Could not fetch game log');
                }
            );
    };

    return service;
})

;
