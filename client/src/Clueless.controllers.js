angular.module('Clueless')

.controller('gameController', function(GameService, gameState, gameMetadata) {

    var vm = this;
    vm.gameState = gameState;
    vm.gameMetadata = gameMetadata;

    vm.addForm = {};
    vm.addForm.name = null;
    vm.addForm.suspect = null;
    vm.addPlayer = function() {
        return GameService.addPlayer(vm.addForm.name, vm.addForm.suspect);
    };

    vm.moveForm = {};
    vm.moveForm.target = Object.keys(vm.gameMetadata.organized_shortname_map.spaces)[0];
    vm.movePlayer = function() {
        return GameService.movePlayer(vm.moveForm.target);
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
