/**
 * Minimal crypto helper for NetEase API.
 * Python calls this via stdin/stdout JSON protocol.
 *
 * Input:  {"endpoint": "...", "data": {...}}
 * Output: {"params": "...", "encSecKey": "..."}
 */
const crypto = require('crypto');

const IV = '0102030405060708';
const NONCE = '0CoJUm6Qyw8W8jud';
const PUBKEY = `-----BEGIN PUBLIC KEY-----
MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQCgtRd8U7jDnAaJVBh+z1s0nHj8
XL2Fiz+WbSkLFSodDNG5o6gQ9MaqTUBMR7g/e/yiA4hJjwDH+kWFj6w3TAh2Cz7o
FxL+XlMqUdiT/ZqG1XhjsSK7uQNHDxVZrLRdRVxIW0Lo8mTLzoSZ0Hi/+nSe3J6I
DCoMt3gV1JZZUh+jKQIDAQAB
-----END PUBLIC KEY-----`;

function aesEncrypt(text, key, iv) {
    const cipher = crypto.createCipheriv('aes-128-cbc', Buffer.from(key), Buffer.from(iv));
    return Buffer.concat([cipher.update(text), cipher.final()]);
}

function rsaEncrypt(text, pubkey) {
    const padding = Buffer.alloc(128 - text.length, 0);
    const padded = Buffer.concat([padding, text]);
    return crypto.publicEncrypt({ key: pubkey, padding: crypto.constants.RSA_NO_PADDING }, padded);
}

function weapi(object) {
    const text = JSON.stringify(object);
    const secKey = crypto.randomBytes(16);

    // AES double-encrypt
    const encText = aesEncrypt(
        Buffer.from(aesEncrypt(Buffer.from(text), NONCE, IV).toString('base64')),
        secKey,
        IV
    ).toString('base64');

    // RSA encrypt reversed secKey
    const encSecKey = rsaEncrypt(Buffer.from(secKey).reverse(), PUBKEY).toString('hex');

    return { params: encText, encSecKey };
}

// Read JSON from stdin
let input = '';
process.stdin.setEncoding('utf8');
process.stdin.on('data', (chunk) => { input += chunk; });
process.stdin.on('end', () => {
    try {
        const req = JSON.parse(input);
        const result = weapi(req.data);
        process.stdout.write(JSON.stringify(result));
    } catch (e) {
        process.stdout.write(JSON.stringify({ error: e.message }));
    }
});
