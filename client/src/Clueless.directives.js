angular.module('Clueless')

.directive('playerBox', function(){
    // Runs during compile
    return {
        restrict: 'E',
        scope: {
            players: '='
        },
        replace: true,
        templateUrl: 'CluelessPlayerOnBoard.html'
    };
})

;