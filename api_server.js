/**
 * NeMusic API Server — wraps NeteaseCloudMusicApi.
 * Forces IPv4 to avoid ECONNRESET issues.
 */
const dns = require('dns');
dns.setDefaultResultOrder('ipv4first');

const { server } = require('./node_modules/NeteaseCloudMusicApi/main');

const PORT = parseInt(process.env.NEMUSIC_API_PORT || '29999');
const HOST = process.env.NEMUSIC_API_HOST || '127.0.0.1';

server.serveNcmApi({
    port: PORT,
    host: HOST,
    checkAuth: false,
});
