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

    #                               | b0 - b2 ω**2 |
    # G(jω) = --------------------------------------------------------------------
    #         sqrt{(ω**4 - (a2 + 1.65 b2)ω**2 + 1.65 b0)**2 + (a1 ω - a3 ω**3)**2}
    # 
    # numerator = abs(
    #     b0 - b2 * ω**2
    # )
    # denominator = numpy.sqrt(
    #     (ω**4 - (a2 + 1.65 * b2) * ω**2 + 1.65 * b0)**2 +
    #     (a1 * ω - a3 * ω**3)**2
    # )
    # return 20 * numpy.log10(numerator / denominator)
