/**
 * Persistent crypto helper for NetEase API.
 * Reads JSON lines from stdin, outputs encrypted params on stdout.
 * Each line: {"data": {...}}
 * Each output: {"params": "...", "encSecKey": "..."}
 * Exit on EOF or stdin close.
 */
var crypto = require('crypto');
var readline = require('readline');

var IV = '0102030405060708';
var NONCE = '0CoJUm6Qyw8W8jud';
var PUBKEY = '-----BEGIN PUBLIC KEY-----\n' +
    'MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQCgtRd8U7jDnAaJVBh+z1s0nHj8\n' +
    'XL2Fiz+WbSkLFSodDNG5o6gQ9MaqTUBMR7g/e/yiA4hJjwDH+kWFj6w3TAh2Cz7o\n' +
    'FxL+XlMqUdiT/ZqG1XhjsSK7uQNHDxVZrLRdRVxIW0Lo8mTLzoSZ0Hi/+nSe3J6I\n' +
    'DCoMt3gV1JZZUh+jKQIDAQAB\n' +
    '-----END PUBLIC KEY-----';

function aesEncrypt(text, key, iv) {
    var cipher = crypto.createCipheriv('aes-128-cbc', Buffer.from(key), Buffer.from(iv));
    return Buffer.concat([cipher.update(text), cipher.final()]);
}

function rsaEncrypt(text, pubkey) {
    var padding = Buffer.alloc(128 - text.length, 0);
    var padded = Buffer.concat([padding, text]);
    return crypto.publicEncrypt(
        { key: pubkey, padding: crypto.constants.RSA_NO_PADDING },
        padded
    );
}

function weapi(object) {
    var text = JSON.stringify(object);
    var secKey = crypto.randomBytes(16);

    var encText = aesEncrypt(
        Buffer.from(aesEncrypt(Buffer.from(text), NONCE, IV).toString('base64')),
        secKey,
        IV
    ).toString('base64');

    var encSecKey = rsaEncrypt(
        Buffer.from(secKey).reverse(),
        PUBKEY
    ).toString('hex');

    return { params: encText, encSecKey: encSecKey };
}

// Read lines from stdin, output encrypted result for each
var rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout,
    terminal: false
});

rl.on('line', function (line) {
    try {
        var req = JSON.parse(line);
        var result = weapi(req.data);
        process.stdout.write(JSON.stringify(result) + '\n');
    } catch (e) {
        process.stdout.write(JSON.stringify({ error: e.message }) + '\n');
    }
});

rl.on('close', function () {
    process.exit(0);
});
