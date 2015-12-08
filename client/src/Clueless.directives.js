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

.directive('playerInfo', function() {
    return {
        restrict: 'A',
        scope: {
            player: '='
        },
        transclude: true,
        replace: true,
        link : function(scope, element, attrs) {
            element.bind('mouseover', function(event) {
                // console.log('Coords:', event.clientX, event.clientY);
                scope.$apply(function() {
                    scope.show = true;
                });
            });
            element.bind('mouseleave', function(event) {
                scope.$apply(function() {
                    scope.show = false;
                });
            });
        },
        templateUrl: 'CluelessBoardPlayerInfoTemplate.html'
    };
})

;