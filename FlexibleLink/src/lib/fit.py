import numpy
import sympy


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

    return #...


def assert_stable(
    a3: float, a2: float, a1: float,
    b2: float, b0: float,
) -> None:
    """
    各伝達関数は ** / (1 + P(s)C(s)) で、どれも計算すると分母多項式が
    Dp(s)Dc(s) + Np(s)Nc(s) となる
    ( P(s) =: Np(s) / Dp(s), C(s) =: Nc(s) / Dc(s) )
    """

    s = sympy.symbols('s')

    Np = b2 * s**2 + b0
    Dp = s**4 + a3 * s**3 + a2 * s**2 + a1 * s
    Nc = 1.65
    Dc = 1

    roots: list = sympy.solve(Dp * Dc + Np * Nc)
    print("roots:", roots)

    if roots.count(0.0) > 0:
        # remove just first 0.0
        roots.remove(0.0)
    if not all([sympy.re(root) < 0 for root in roots]):
        raise ValueError("The system is not stable: roots are not all in the left half plane.")
    if not all([roots.count(root) == 1 for root in roots]):
        raise ValueError("The system is not stable: has multiple roots.")
    print("The system is stable.")
    
