angular.module('Clueless')

.factory('GameService', function(CluelessAPI, $http, localStorageService) {
    var service = {};

    // Metadata services
    service.metadata = $http.get(CluelessAPI + '/meta')
                         .then(
                             function(response) {
                                 return response.data;
                             },
                            function(response) {
                                 toastr.error('Could not get board metadata');
                             }
                         );
    service.getMetadata = function() {
        return service.metadata;
    };
    service.setMetadata = function(data) {
        service.metadata = data;
        return true;
    };
    service.expandShortname = function(shortname) {
        return service.metadata.shortname_map[shortname];
    };

    // State services
    service.state = $http.get(CluelessAPI)
                         .then(
                             function(response) {
                                 return response.data;
                             },
                            function(response) {
                                 toastr.error('Could not get board state');
                             }
                         );
    service.getState = function() {
        return service.state;
    };

    // Add player and set local storage with token
    service.addPlayer = function(playerName, suspect) {
        data = {
            'name': playerName,
            'suspect': suspect
        };

        return $http.post(CluelessAPI + '/players', data)
            .then(
                function(response) {
                    toastr.success('Created new player');
                    localStorageService.set('player_token', response.data.player_token);
                    return response.data;
                },
               function(response) {
                    toastr.error(response.data.message);
                }
            );
    };

    // Set player token

    // Check if player's been added
    service.addedPlayer = function() {
        return localStorageService.get('player_token') ? true : false;
    };

    // Get player sheet

    // Update player sheet

    // Move player
    service.movePlayer = function(target_space) {
        data = {
            'token': localStorageService.get('player_token'),
            'space': target_space
        };

        console.log(data);

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

    // Make suggestion

    // Make accusation

    // End turn

    return service;
})

.factory('LogsService', function(CluelessAPI, $http) {
    var service = {};

    service.logs = $http.get(CluelessAPI + '/logs')
                         .then(
                             function(response) {
                                return response.data;
                             },
                            function(response) {
                                toastr.error('Could not get logs');
                             }
                         );

    service.getLogs = function() {
        return service.logs;
    };

    return service;
})

;