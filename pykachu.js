var SERVER_PORT = process.env.SERVER_PORT || 8080;
var REDIS_SERVER = process.env.REDIS_SERVER || "localhost";
var REDIS_PORT = process.env.REDIS_PORT || 6379;

var http = require('http');
var redis = require("redis");
var socket = require("socket.io");

var pykachu_prefix = "pykachu";

var server = http.createServer();
server.listen(SERVER_PORT);

var io = socket.listen(server, {log: false });
var client = redis.createClient(REDIS_PORT, REDIS_SERVER);
var jobs_rodando = [];

io.sockets.on('connection', function (socket) {

    socket.on(pykachu_prefix + '_remove', function (data) {
        console.log("Removendo Key:", data.key);
        client.del(data.key);
    });
    console.log("conectando novo usuario");
});

setInterval(function () {
    client.keys(pykachu_prefix + "*", function (err, keys) {
        keys.forEach(function (key, pos) {
            client.hgetall(key, function (err, obj) {
                if (obj) {
                    obj.key = key;
                    io.sockets.emit(pykachu_prefix, obj);
                }
            });
        });
        if (jobs_rodando) {
            // depois o que havera em remover serão as keys a serem removidas na interface
            var remover = jobs_rodando.slice();

            for (var i = 0; i < keys.length; i++) {
                var idx = remover.indexOf(keys[i]);
                if (idx !== -1) {
                   remover.splice(idx, 1);
                }
            }
            for (var j = 0; j < remover.length; j++) {
                // FIXME: delete é uma palavra reservada!!
                io.sockets.emit(pykachu_prefix, {delete: remover[j], key:remover[j]});
            }
        }
        jobs_rodando = keys.slice();
    });
}, 100);

setInterval(function () {
    console.log("Jobs Rodando:" + jobs_rodando.length);
}, 5000);
