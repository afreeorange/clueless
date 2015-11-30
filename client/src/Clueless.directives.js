angular.module('Clueless')

.directive('playerBox', function(){
    // Runs during compile
    return {
        restrict: 'E',
        scope: {
            players: '='
        },
        replace: true,
        controller: function(GameService) {
            var vm = this;
            vm.expandShortname = function(shortname) {
                return GameService.getMetadata().shortname_map[shortname];
            };
        },
        controllerAs: 'pbc',
        templateUrl: 'CluelessPlayerOnBoard.html'
    };
})

;