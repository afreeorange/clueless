angular.module('Clueless')

.controller('gameController', function(GameService, gameState, $interval) {

    var vm = this;
    vm.gameState = gameState;
    // vm.gameMetadata = gameMetadata;
    vm.gameMetadata = GameService.getMetadata();

    // Resolve shortnames
    vm.expandShortname = function(shortname) {
        return vm.gameMetadata.shortname_map[shortname];
    };

    // Determine of the client is already added to the board
    vm.addedPlayer = function() {
        return GameService.addedPlayer();
    };

    // Determine if the client is in the game
    vm.playerInTheGame = function() {
        if (vm.playerData) {
            return vm.playerData.in_the_game;
        }
        return null;
    };

    // Add player
    vm.addForm = {};
    vm.addForm.name = null;
    vm.addForm.suspect = null;
    vm.addPlayer = function() {
        return GameService.addPlayer(vm.addForm.name, vm.addForm.suspect);
    };

    // Player data
    vm.playerData = GameService.getPlayerData();

    // Move 
    vm.moveForm = {};
    vm.moveForm.target = Object.keys(vm.gameMetadata.organized_shortname_map.spaces)[0];
    vm.movePlayer = function() {
        return GameService.movePlayer(vm.moveForm.target);
    };

    // Suggest
    vm.suggestForm = {};
    vm.suggestForm.suspect = Object.keys(vm.gameMetadata.organized_shortname_map.suspects)[0];
    vm.suggestForm.weapon = Object.keys(vm.gameMetadata.organized_shortname_map.weapons)[0];
    vm.makeSuggestion = function() {
        return GameService.makeSuggestion(vm.suggestForm.suspect, vm.suggestForm.weapon);
    };

    // Accuse
    vm.accuseForm = {};
    vm.accuseForm.suspect = Object.keys(vm.gameMetadata.organized_shortname_map.suspects)[0];
    vm.accuseForm.weapon = Object.keys(vm.gameMetadata.organized_shortname_map.weapons)[0];
    vm.accuseForm.room = Object.keys(vm.gameMetadata.organized_shortname_map.rooms)[0];
    vm.makeAccusation = function() {
        return GameService.makeAccusation(vm.accuseForm.suspect, vm.accuseForm.weapon, vm.accuseForm.room);
    };

    // End turn
    vm.endTurn = function() {
        return GameService.endTurn();
    };

    vm.isCurrentTurn = function() {
        return GameService.isCurrentTurn();
    };

    $interval(function(){
        GameService.getState().then(
            function(response) {
                vm.gameState = response;
            },
            function(response) {
                return;
            });

        if (vm.addedPlayer()) {
            vm.playerData = GameService.refreshPlayerData();    
        }

    }.bind(this), 5000);  

})

.controller('logsController', function(LogsService, logs, $interval) {

    var vm = this;
    vm.logs = logs;

    $interval(function(){
        LogsService.getLogs().then(
            function(response) {
                vm.logs = response;
            },
            function(response) {
                return;
            });
    }.bind(this), 5000);  

})

;
