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

    return #


def assert_stable(
    a3: float, a2: float, a1: float,
    b2: float, b0: float,
) -> None:
    """
    Assert that the system is stable.
    """
    # if a3 < 0 or a2 < 0 or a1 < 0 or b2 < 0 or b0 < 0:
    #     raise ValueError("The system is not stable.")
    # 
    # todo

    """
    Check the characteristic polynomial is stable.
    The characteristic polynomial is given by

    s^4 + a3 * s^3 + a2 * s^2 + a1 * s = 0

    The system is stable if all the roots of the characteristic polynomial have negative real parts.
    The Routh-Hurwitz stability criterion is used to check the stability.
    """

    s = sympy.symbols('s')
    roots: list = sympy.solve(s**4 + a3 * s**3 + a2 * s**2 + a1 * s)
    print("roots:", roots)

    if not roots.count(0.0) == 1: # s * (...) = 0
        raise ValueError("One root must be 0.")
    roots.remove(0.0)
    if not all([sympy.re(root) < 0 for root in roots]):
        raise ValueError("The system is not stable.")
    print("The system is stable.")
    
    
