angular.module('Clueless')

.directive('playerBox', function(){
    return {
        restrict: 'E',
        scope: {
            players: '='
        },
        replace: true,
        controller: function(GameService) {
            var vm = this;
            vm.shortNameMap = null;

            GameService.getMetadata().then(
                    function(response) {
                        vm.shortNameMap = response;
                    }, 
                    function() {});

            vm.expandShortname = function(shortname) {
                return vm.shortNameMap.shortname_map[shortname];
            };
        },
        controllerAs: 'pbc',
        templateUrl: 'CluelessPlayerOnBoard.html'
    };
})

;