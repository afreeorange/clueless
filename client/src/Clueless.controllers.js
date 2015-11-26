angular.module('Clueless')

.controller('boardController', function(BoardService, boardState, boardMetadata, $interval) {

    var vm = this;
    vm.boardState = boardState;
    vm.playerName = null;
    vm.suspect = null;

    vm.suspectList = boardMetadata.data.organized_shortname_map.suspects;
    vm.roomList = boardMetadata.data.organized_shortname_map.rooms;
    vm.weaponList = boardMetadata.data.organized_shortname_map.weapons;

    vm.space = null;
    vm.suggestion_suspect = null;
    vm.suggestion_weapon = null;
    vm.suggestion_room = null;

    vm.addedPlayer = function() {
        return BoardService.addedPlayer();
    };

    vm.addPlayer = function() {
        return BoardService.addPlayer(vm.playerName, vm.suspect);
    };

    vm.movePlayer = function() {
        return BoardService.movePlayer(vm.room);
    };

    $interval(function(){
        BoardService.getState().then(
            function(response) {
                vm.boardState = response;
            },
            function(response) {
                return;
            });
    }.bind(this), 2000);  

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
    }.bind(this), 2000);  

})

;
