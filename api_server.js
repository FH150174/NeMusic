/**
 * NeMusic API Server — wraps NeteaseCloudMusicApi.
 * Forces IPv4 to avoid ECONNRESET issues.
 * Auto-finds global NeteaseCloudMusicApi installation.
 */
var dns = require('dns');
dns.setDefaultResultOrder('ipv4first');

var path = require('path');
var Module = require('module');

// Find global node_modules path
var globalPaths = [];
try {
    var npmRoot = require('child_process').execSync('npm root -g', { encoding: 'utf8' }).trim();
    if (npmRoot) globalPaths.push(npmRoot);
} catch (e) {}

// Add common global paths
var homeDrive = process.env.HOMEDRIVE || 'C:';
globalPaths.push(path.join(homeDrive, 'Users', process.env.USERNAME || 'FH', 'AppData', 'Roaming', 'npm', 'node_modules'));
globalPaths.push('./node_modules');

// Override require to search these paths
var originalResolve = Module._resolveFilename;
Module._resolveFilename = function (request, parent) {
    for (var i = 0; i < globalPaths.length; i++) {
        try {
            var fp = path.join(globalPaths[i], request);
            return originalResolve.call(this, fp, parent);
        } catch (e) {}
    }
    return originalResolve.call(this, request, parent);
};

var server = require('NeteaseCloudMusicApi').server;

var PORT = parseInt(process.env.NEMUSIC_API_PORT || '29999');
var HOST = process.env.NEMUSIC_API_HOST || '127.0.0.1';

server.serveNcmApi({
    port: PORT,
    host: HOST,
    checkAuth: false,
});
