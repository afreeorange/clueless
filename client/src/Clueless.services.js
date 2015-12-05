angular.module('Clueless')

.factory('SocketService', function (socketFactory, CluelessSocketServer) {
    return socketFactory({
        ioSocket: io.connect(CluelessSocketServer)
    });
})

.factory('GameService', function(CluelessAPI, $http, localStorageService) {
    var service = {};

    // Metadata services
    service.metadata = null;
    service.getMetadata = function() {
        return service.metadata;
    };
    service.setMetadata = function(data) {
        service.metadata = data;
        return true;
    };

    // State services
    service.state = null;
    service.getState = function() {
        service.state = $http.get(CluelessAPI)
                             .then(
                                 function(response) {
                                     return response.data;
                                 },
                                function(response) {
                                     toastr.error('Could not get board state');
                                 }
                             );
        return service.state;
    };
    service.setState = function(data) {
        service.state = data;
        return true;
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
                    localStorageService.set('player_token', response.data.player_token);
                    localStorageService.set('suspect', response.data.suspect);

                    return response.data;
                },
               function(response) {
                    toastr.error(response.data.message);
                }
            );
    };

    // Get player information
    service.playerData = null;
    service.getPlayerData = function() {
        return service.playerData;
    };
    service.setPlayerData = function(data) {
        service.playerData = data;
        return true;
    };
    service.refreshPlayerData = function() {
        player_token = localStorageService.get('player_token');

        $http.get(CluelessAPI + '/players/' + player_token)
           .then(
               function(response) {
                   service.playerData = response.data;
               },
               function(response) {
                   return;
               }
           );

        return service.playerData;
    };

    // Check if player's been added
    service.addedPlayer = function() {
        return localStorageService.get('player_token') ? true : false;
    };

    // Move player
    service.movePlayer = function(target_space) {
        data = {
            'token': localStorageService.get('player_token'),
            'space': target_space
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

    // Make suggestion
    service.makeSuggestion = function(suspect, weapon) {
        data = {
            'token': localStorageService.get('player_token'),
            'suspect': suspect,
            'weapon': weapon
        };

        return $http.put(CluelessAPI + '/suggest', data)
            .then(
                function(response) {
                    toastr.success('Sent suggestion');
                    return response.data;
                },
               function(response) {
                    toastr.error(response.data.message);
                }
            );
    };

    // Make accusation
    service.makeAccusation = function(suspect, weapon, room) {
        data = {
            'token': localStorageService.get('player_token'),
            'suspect': suspect,
            'weapon': weapon,
            'room': room
        };

        return $http.put(CluelessAPI + '/accuse', data)
            .then(
                function(response) {
                    toastr.success('Sent accusation');
                    return response.data;
                },
               function(response) {
                    toastr.error(response.data.message);
                }
            );
    };

    // End turn
    service.endTurn = function() {
        data = {
            'token': localStorageService.get('player_token')
        };

        return $http.put(CluelessAPI + '/end_turn', data)
            .then(
                function(response) {
                    toastr.success('Ended turn');
                    return response.data;
                },
               function(response) {
                    toastr.error(response.data.message);
                }
            );
    };

    return service;
})

.factory('LogsService', function(CluelessAPI, $http) {
    var service = {};

    service.logs = null;
    service.getLogs = function() {
        service.logs = $http.get(CluelessAPI + '/logs')
                         .then(
                             function(response) {
                                return response.data;
                             },
                            function(response) {
                                toastr.error('Could not get logs');
                             }
                         );
        return service.logs;
    };

    return service;
})

;