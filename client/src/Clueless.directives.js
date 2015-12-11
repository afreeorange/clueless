angular.module('Clueless')

.directive('playerBox', function() {
    return {
        restrict: 'E',
        scope: {
            players: '='
        },
        replace: true,
        templateUrl: 'templates/playerOnBoard.html'
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
        link: function(scope, element, attrs) {
            element.bind('mouseover', function(event) {
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
        templateUrl: 'templates/boardPlayerInfoTemplate.html'
    };
})

;