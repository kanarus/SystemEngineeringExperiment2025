import numpy


def BodeGainCurve(
    ω: float,
    a3: float, a2: float, a1: float,
    b2: float, b0: float,
) -> float:
    C = lambda _: 1.65
    P = lambda s: (b2 * s**2 + b0) / (s**4 + a3 * s**3 + a2 * s**2 + a1 * s)
    G = lambda s: P(s) / (1 + P(s) * C(s))
    
    return 20 * numpy.log10(abs(G(1j * ω)))
