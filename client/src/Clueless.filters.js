angular.module('Clueless')

.filter('removeThe', function() {
    return function(input) {
        if (input) {
            return input.replace('The ', '');
        }
        return null;
    };
})

;