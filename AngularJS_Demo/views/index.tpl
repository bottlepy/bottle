<!DOCTYPE html>

<html ng-app="app">
    <head>
        <title>Index Main</title>
        <script src="https://ajax.googleapis.com/ajax/libs/angularjs/1.5.8/angular.min.js"></script>
    </head>
    <body>
        [{message}] <!--- Simple Template Directive --->
        <form action="">
            <input type="text" name="" id="" ng-model="input">
            <p>{{input}}</p> <!--- AngularJS Directive --->
        </form>
        <script>
            var app = angular.module('app',[])
        </script>
    </body>
</html>