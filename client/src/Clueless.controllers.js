angular.module('Clueless')

.controller('boardController', function(BoardService, boardState, boardMetadata) {

    var vm = this;
    vm.boardState = boardState;
    vm.suspectList = boardMetadata.data.organized_shortname_map.suspects;
    vm.roomList = boardMetadata.data.organized_shortname_map.rooms;

    vm.space = null;

    vm.addedPlayer = function() {
        return BoardService.addedPlayer();
    };

    vm.addPlayer = function() {
        return BoardService.addPlayer(vm.playerName, vm.suspect);
    };

    vm.movePlayer = function() {
        return BoardService.movePlayer(vm.room);
    };

})

.controller('logsController', function(logs) {

    var vm = this;
    vm.logs = logs;

})

;
