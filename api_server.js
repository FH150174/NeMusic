/**
 * NeMusic API Server — wraps NeteaseCloudMusicApi.
 * Forces IPv4 to avoid ECONNRESET issues.
 *
 * Uses global NeteaseCloudMusicApi installation.
 */
var dns = require('dns');
dns.setDefaultResultOrder('ipv4first');

// Try local node_modules first, then global
var ncmPath;
try {
    ncmPath = './node_modules/NeteaseCloudMusicApi/main';
    require.resolve(ncmPath);
} catch (e) {
    ncmPath = 'NeteaseCloudMusicApi';
}

var server = require(ncmPath).server;

var PORT = parseInt(process.env.NEMUSIC_API_PORT || '29999');
var HOST = process.env.NEMUSIC_API_HOST || '127.0.0.1';

server.serveNcmApi({
    port: PORT,
    host: HOST,
    checkAuth: false,
});
