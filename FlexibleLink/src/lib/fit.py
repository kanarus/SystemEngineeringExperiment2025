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


def NiquistCurve(
    x: float,
    a3: float, a2: float, a1: float,
    b2: float, b0: float,
) -> float:
    """
    Nyquist curve for a given set of parameters.

    x = Re(G(jω)) = |G(jω)| * cos(∠G(jω))
    y = Im(G(jω)) = |G(jω)| * sin(∠G(jω))

    then

    ∠G(jω) = arccos(x / |G(jω)|)

    so

    y = |G(jω)| * sin(arccos(x / |G(jω)|)
    """
    
    C = lambda _: 1.65
    P = lambda s: (b2 * s**2 + b0) / (s**4 + a3 * s**3 + a2 * s**2 + a1 * s)
    G = lambda s: P(s) / (1 + P(s) * C(s))

    x_from_ω = lambda ω: numpy.real(G(1j * ω))
    y_from_ω = lambda ω: numpy.imag(G(1j * ω))

    return 
    
