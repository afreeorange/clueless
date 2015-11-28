angular.module('Clueless')

.controller('gameController', function(GameService, gameState, gameMetadata) {

    var vm = this;
    vm.gameState = gameState;
    vm.gameMetadata = gameMetadata;

    // Resolve shortnames
    vm.expandShortname = function(shortname) {
        console.log(vm.expandShortname(shortname));
        return vm.expandShortname(shortname);
    };

    // Add player
    vm.addForm = {};
    vm.addForm.name = null;
    vm.addForm.suspect = null;
    vm.addPlayer = function() {
        return GameService.addPlayer(vm.addForm.name, vm.addForm.suspect);
    };

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
    vm.suggestForm.room = Object.keys(vm.gameMetadata.organized_shortname_map.rooms)[0];
    vm.makeSuggestion = function() {
        return GameService.makeSuggestion(vm.suggestForm.suspect, vm.suggestForm.weapon, vm.suggestForm.room);
    };

    // End turn
    vm.endTurn = function() {
        return GameService.endTurn();
    };

    vm.isCurrentTurn = function() {
        return GameService.isCurrentTurn();
    };

})

.controller('logsController', function(LogsService, logs, $interval) {

    var vm = this;
    vm.logs = logs;

    // $interval(function(){
    //     LogsService.getLogs().then(
    //         function(response) {
    //             vm.logs = response;
    //         },
    //         function(response) {
    //             return;
    //         });
    // }.bind(this), 1000);  

})

;
