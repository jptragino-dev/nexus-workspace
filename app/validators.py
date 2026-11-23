import re


def only_digits(v: str) -> str:
    return re.sub(r"\D", "", v or "")


def valid_cpf(v: str) -> bool:
    d = only_digits(v)
    if len(d) != 11 or len(set(d)) == 1:
        return False
    for i in (9, 10):
        s = sum(int(d[j]) * (i + 1 - j) for j in range(i))
        if (s * 10 % 11) % 10 != int(d[i]):
            return False
    return True


def valid_cnpj(v: str) -> bool:
    d = only_digits(v)
    if len(d) != 14 or len(set(d)) == 1:
        return False
    w1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    for n, w in ((12, w1), (13, [6] + w1)):
        r = sum(int(d[i]) * w[i] for i in range(n)) % 11
        if int(d[n]) != (0 if r < 2 else 11 - r):
            return False
    return True
