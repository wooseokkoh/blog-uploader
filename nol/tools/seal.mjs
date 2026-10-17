// 명단 데이터(JSON)를 비밀번호로 암호화해 nol/data.bin 을 만들거나, 반대로 풀어 JSON으로 꺼냅니다.
// 사용법:
//   node nol/tools/seal.mjs seal   <원본.json> <비밀번호>   → nol/data.bin 생성
//   node nol/tools/seal.mjs unseal <비밀번호> <저장할.json>  → nol/data.bin 을 풀어 저장
// 원본 JSON(평문 명단)은 공개 저장소에 절대 올리지 마세요.
import { readFileSync, writeFileSync } from 'node:fs';
import { webcrypto as crypto } from 'node:crypto';

const MAGIC = new TextEncoder().encode('NOL1');
const ITER = 250000;
const OUT = new URL('../data.bin', import.meta.url);

async function key(pw, salt) {
  const base = await crypto.subtle.importKey('raw', new TextEncoder().encode(pw), 'PBKDF2', false, ['deriveKey']);
  return crypto.subtle.deriveKey({ name: 'PBKDF2', salt, iterations: ITER, hash: 'SHA-256' }, base,
    { name: 'AES-GCM', length: 256 }, false, ['encrypt', 'decrypt']);
}

const [mode, a, b] = process.argv.slice(2);
if (mode === 'seal') {
  const plain = readFileSync(a);
  const salt = crypto.getRandomValues(new Uint8Array(16));
  const iv = crypto.getRandomValues(new Uint8Array(12));
  const ct = new Uint8Array(await crypto.subtle.encrypt({ name: 'AES-GCM', iv }, await key(b, salt), plain));
  writeFileSync(OUT, Buffer.concat([MAGIC, salt, iv, ct]));
  console.log('sealed →', OUT.pathname, ct.length, 'bytes');
} else if (mode === 'unseal') {
  const buf = new Uint8Array(readFileSync(OUT));
  const salt = buf.slice(4, 20), iv = buf.slice(20, 32);
  const pt = await crypto.subtle.decrypt({ name: 'AES-GCM', iv }, await key(a, salt), buf.slice(32));
  writeFileSync(b, Buffer.from(pt));
  console.log('unsealed →', b);
} else {
  console.log('usage: seal <in.json> <pw> | unseal <pw> <out.json>');
}
