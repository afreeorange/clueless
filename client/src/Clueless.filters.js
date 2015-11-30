angular.module('Clueless')

.filter('removeThe', function() {
    return function(input) {
        return input.replace('The ', '');
    };
})

;