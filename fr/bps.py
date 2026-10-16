"""Encodeur / décodeur BPS minimal (format de patch de byuu, lu par la page web).

Encodage glouton : à chaque position de la ROM cible, on cherche la plus longue
copie possible dans la source (les deux ROMs Europe bout à bout), puis dans la
partie déjà écrite de la cible (répétitions, zones vides). Sinon, octets
littéraux.
"""
import zlib

SOURCE_READ, TARGET_READ, SOURCE_COPY, TARGET_COPY = range(4)
K = 12          # longueur des clés de recherche
MIN_COPY = 16   # copie minimale (sinon littéral)
MAX_CANDIDATES = 8


def _varint(n):
    out = bytearray()
    while True:
        x = n & 0x7f
        n >>= 7
        if n == 0:
            out.append(0x80 | x)
            return out
        out.append(x)
        n -= 1


def _signed(n):
    return _varint((abs(n) << 1) | (1 if n < 0 else 0))


def _index(data, step=1):
    idx = {}
    for i in range(0, len(data) - K, step):
        key = data[i:i + K]
        lst = idx.get(key)
        if lst is None:
            idx[key] = [i]
        elif len(lst) < MAX_CANDIDATES:
            lst.append(i)
    return idx


def _match_len(a, ai, b, bi, limit):
    n = 0
    while n < limit and a[ai + n] == b[bi + n]:
        n += 1
    return n


def encode(source, target):
    source, target = bytes(source), bytes(target)
    out = bytearray(b'BPS1')
    out += _varint(len(source)) + _varint(len(target)) + _varint(0)
    src_idx = _index(source)
    tgt_idx = {}
    src_rel = tgt_rel = 0
    literal = bytearray()
    lit_start = 0

    def flush():
        nonlocal literal
        if literal:
            out.extend(_varint(((len(literal) - 1) << 2) | TARGET_READ))
            out.extend(literal)
            literal = bytearray()

    i, n = 0, len(target)
    while i < n:
        best_len, best_kind, best_pos = 0, None, 0
        # Même position dans la source
        if i < len(source):
            l = _match_len(source, i, target, i, min(len(source), n) - i)
            if l >= MIN_COPY:
                best_len, best_kind, best_pos = l, SOURCE_READ, i
        if i + K <= n:
            key = target[i:i + K]
            for p in src_idx.get(key, ()):
                l = _match_len(source, p, target, i, min(len(source) - p, n - i))
                if l > best_len:
                    best_len, best_kind, best_pos = l, SOURCE_COPY, p
            for p in tgt_idx.get(key, ()):
                l = _match_len(target, p, target, i, n - i)
                if l > best_len:
                    best_len, best_kind, best_pos = l, TARGET_COPY, p
        # Répétition d'un même octet (zones vides)
        if i > 0 and target[i] == target[i - 1]:
            l = _match_len(target, i - 1, target, i, n - i)
            if l > best_len:
                best_len, best_kind, best_pos = l, TARGET_COPY, i - 1

        if best_len >= MIN_COPY:
            flush()
            out.extend(_varint(((best_len - 1) << 2) | best_kind))
            if best_kind == SOURCE_COPY:
                out.extend(_signed(best_pos - src_rel))
                src_rel = best_pos + best_len
            elif best_kind == TARGET_COPY:
                out.extend(_signed(best_pos - tgt_rel))
                tgt_rel = best_pos + best_len
            end = i + best_len
        else:
            literal.append(target[i])
            end = i + 1
        # Indexer la cible écrite (une position sur 4 suffit pour les copies internes)
        for j in range(i - (i % 4), end, 4):
            if j + K <= n and j >= 0:
                key = target[j:j + K]
                lst = tgt_idx.get(key)
                if lst is None:
                    tgt_idx[key] = [j]
                elif len(lst) < MAX_CANDIDATES:
                    lst.append(j)
        i = end
    flush()
    out += (zlib.crc32(source) & 0xffffffff).to_bytes(4, 'little')
    out += (zlib.crc32(target) & 0xffffffff).to_bytes(4, 'little')
    out += (zlib.crc32(out) & 0xffffffff).to_bytes(4, 'little')
    return bytes(out)


def decode(source, patch):
    """Décodeur de vérification (le même algorithme que la page web)."""
    assert patch[:4] == b'BPS1'
    pos = 4

    def varint():
        nonlocal pos
        data, shift = 0, 1
        while True:
            x = patch[pos]
            pos += 1
            data += (x & 0x7f) * shift
            if x & 0x80:
                return data
            shift <<= 7
            data += shift

    ssize, tsize, msize = varint(), varint(), varint()
    pos += msize
    target = bytearray(tsize)
    out = src_rel = tgt_rel = 0
    while pos < len(patch) - 12:
        data = varint()
        cmd, length = data & 3, (data >> 2) + 1
        if cmd == SOURCE_READ:
            target[out:out + length] = source[out:out + length]
            out += length
        elif cmd == TARGET_READ:
            target[out:out + length] = patch[pos:pos + length]
            pos += length
            out += length
        else:
            d = varint()
            off = -(d >> 1) if d & 1 else d >> 1
            if cmd == SOURCE_COPY:
                src_rel += off
                target[out:out + length] = source[src_rel:src_rel + length]
                src_rel += length
                out += length
            else:
                tgt_rel += off
                for _ in range(length):     # peut se chevaucher
                    target[out] = target[tgt_rel]
                    out += 1
                    tgt_rel += 1
    assert zlib.crc32(target) & 0xffffffff == int.from_bytes(patch[-8:-4], 'little')
    return bytes(target)
