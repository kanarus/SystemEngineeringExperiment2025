import argparse
import sympy


a3 = 6.33756229e+01
a2 = 1.63223813e+03
a1 = 4.37995800e+04
b2 = 9.55823457e+01
b0 = 6.62196269e+04


def main():
    a = argparse.ArgumentParser()
    a.add_argument('--r1', type=float, nargs=2)
    a.add_argument('--r2', type=float, nargs=2)

    r1, r2 = a.parse_args().r1, a.parse_args().r2
    if r1 is None or r2 is None:
        raise ValueError("r1 and r2 must be provided")
    
    r1, r2 = [complex(r[0], r[1]) for r in (r1, r2)]

    if any(r.real >= 0 for r in (r1, r2)):
        raise ValueError("All roots must have negative real parts")

    print("specified roots:", r1, r2)

    r3_real = -a2/2 - r1.real - r2.real

    r4, r5 = r1.conjugate(), r2.conjugate()

    print("a2 vs -2(real(r1) + real(r2) + real(r3)):",  
        a2,
        -2 * (r1.real + r2.real + r3_real)
    )

    r3_imag = sympy.var('r3_imag')

    r3 = r3_real + 1j * r3_imag
    r6 = r3.conjugate()

    print("r3:", r3)
    print("r6:", r6)

    s = sympy.symbols('s')

    # actual_characteristic_poly = sympy.poly((s-r1) * (s-r2) * (s-r3) * (s-r4) * (s-r5) * (s-r6))
    # actual_coeffs = actual_characteristic_poly.all_coeffs()
    # 
    # print("coeffs:", actual_coeffs)



if __name__ == '__main__':
    main()
