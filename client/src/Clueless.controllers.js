angular.module('Clueless')

.controller('gameController', function(GameService, SocketService, gameState, gameMetadata) {

    var vm = this;
    vm.gameState = gameState;
    vm.gameMetadata = gameMetadata;
    vm.playerData = null;

    // Listen for changes to board state & player data
    SocketService.on('board:state', function(message) {
        vm.gameState = message;
    });

    SocketService.on('board:playerdata', function(message) {
        vm.playerData = message;
    });

    // Resolve shortnames
    vm.expandShortname = function(shortname) {
        return vm.gameMetadata.shortname_map[shortname];
    };

    // Add player
    vm.addForm = {};
    vm.addForm.name = null;
    vm.addForm.suspect = null;
    vm.addPlayer = function() {
        GameService.addPlayer(vm.addForm.name, vm.addForm.suspect)
                   .then(
                        function(response) {
                            SocketService.emit('board:playerdata', {'token': GameService.getPlayerToken()});
                        },
                        function(response) {}
                    );
    };

    // Move 
    vm.moveForm = {};
    vm.moveForm.target = Object.keys(vm.gameMetadata.organized_shortname_map.spaces)[0];
    vm.movePlayer = function() {
        return GameService.movePlayer(vm.moveForm.target)
                   .then(
                        function(response) {
                            SocketService.emit('board:playerdata', {'token': GameService.getPlayerToken()});
                        },
                        function(response) {}
                    );
    };

    // Suggest
    vm.suggestForm = {};
    vm.suggestForm.suspect = Object.keys(vm.gameMetadata.organized_shortname_map.suspects)[0];
    vm.suggestForm.weapon = Object.keys(vm.gameMetadata.organized_shortname_map.weapons)[0];
    vm.makeSuggestion = function() {
        return GameService.makeSuggestion(vm.suggestForm.suspect, vm.suggestForm.weapon)
                   .then(
                        function(response) {
                            SocketService.emit('board:playerdata', {'token': GameService.getPlayerToken()});
                        },
                        function(response) {}
                    );
    };

    // Accuse
    vm.accuseForm = {};
    vm.accuseForm.suspect = Object.keys(vm.gameMetadata.organized_shortname_map.suspects)[0];
    vm.accuseForm.weapon = Object.keys(vm.gameMetadata.organized_shortname_map.weapons)[0];
    vm.accuseForm.room = Object.keys(vm.gameMetadata.organized_shortname_map.rooms)[0];
    vm.makeAccusation = function() {
        return GameService.makeAccusation(vm.accuseForm.suspect, vm.accuseForm.weapon, vm.accuseForm.room)
                   .then(
                        function(response) {
                            SocketService.emit('board:playerdata', {'token': GameService.getPlayerToken()});
                        },
                        function(response) {}
                    );
    };

    // End turn
    vm.endTurn = function() {
        return GameService.endTurn()
                   .then(
                        function(response) {
                            SocketService.emit('board:playerdata', {'token': GameService.getPlayerToken()});
                        },
                        function(response) {}
                    );
    };

    vm.isCurrentTurn = function() {
        return GameService.isCurrentTurn();
    };

})

.controller('logsController', function(logs, SocketService) {

    var vm = this;
    vm.logs = logs;

    SocketService.on('board:log', function(message) {
        vm.logs = message; 
    });

})

;
