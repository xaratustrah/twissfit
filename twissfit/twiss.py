# -*- coding: utf-8 -*-
"""
TWISS parameter calculations

2019

Xaratustrah (S. Sanjari)
based on method / calculations by: H. Weick

Reference:

H. Wollnik, Optics of Charged Particles, Academic Press, 1987, pages 52 and 154.
In the above reference, B, A and C are beta, alpha and gamma Twiss / Courant-Snyder parameters.



"""

import numpy as np

L_DRIFT = 2.216  # m
L_GEO_QUAD = 1  # m
R_QUAD = 0.085  # m
I1A_NORM = 0.00092
BRHO = 8.151048  # Tm
B = -0.23044572  # T


def get_gamma(beta, alpha):
    return (1 + alpha**2) / beta


def calculate_k_prime_l_quad():
    return B * L_GEO_QUAD / R_QUAD / BRHO


def get_drift():
    return np.array([[1, L_DRIFT], [0, 1]])


def get_kappa_quad(k_prime_l_quad):
    return np.sqrt(np.abs(k_prime_l_quad / L_GEO_QUAD))


def get_ff(k_prime_l_quad):
    return np.array([[1 - I1A_NORM * k_prime_l_quad / L_GEO_QUAD, 0], [0, 1 + I1A_NORM * k_prime_l_quad / L_GEO_QUAD]])


def get_mq_hor(kappa_quad):
    return np.array([[np.cosh(kappa_quad * L_GEO_QUAD), 1 / kappa_quad * np.sinh(kappa_quad * L_GEO_QUAD)], [kappa_quad * np.sinh(kappa_quad * L_GEO_QUAD), np.cosh(kappa_quad * L_GEO_QUAD)]])


def get_mq_vert(kappa_quad):
    return np.array([[np.cos(kappa_quad * L_GEO_QUAD), 1 / kappa_quad * np.sin(kappa_quad * L_GEO_QUAD)], [-kappa_quad * np.sin(kappa_quad * L_GEO_QUAD), np.cos(kappa_quad * L_GEO_QUAD)]])


def get_xfer_hor(ff, mq_hor):
    # (x|x), (x|a)
    # (a|x), (a|a)
    return get_drift() @ np.flip(ff).T @ mq_hor @ ff


def get_xfer_vert(ff, mq_vert):
    # (x|x), (x|a)
    # (a|x), (a|a)
    return get_drift() @ ff @ mq_vert @ np.flip(ff).T


def get_twiss_matrix(xfer):
    ss = np.array([])
    ss = np.append(ss, xfer[0, 0]**2)
    ss = np.append(ss, -2 * xfer[0, 0] * xfer[0, 1])
    ss = np.append(ss, xfer[0, 1]**2)
    ss = np.append(ss, -xfer[0, 0] * xfer[1, 0])
    ss = np.append(ss, xfer[0, 0] * xfer[1, 1] + xfer[0, 1] * xfer[1, 0])
    ss = np.append(ss, -xfer[0, 1] * xfer[1, 1])
    ss = np.append(ss, xfer[1, 0]**2)
    ss = np.append(ss, -2 * xfer[1, 0] * xfer[1, 1])
    ss = np.append(ss, xfer[1, 1]**2)
    return np.reshape(ss, (3, 3))


def transform(beta0, alpha0, xfer):
    inp = np.array([beta0, alpha0, get_gamma(beta0, alpha0)]).reshape(3, 1)
    mat = get_twiss_matrix(xfer) @ inp
    beta1 = mat[0, 0]
    alpha1 = mat[1, 0]
    gamma1 = mat[2, 0]
    return beta1, alpha1, gamma1


def solve_equation_system(result_matrix):
    nrows, ncols = np.shape(result_matrix)

    # solving a X = b for x-plane
    a_hor = np.array([])
    b_hor = np.array([])
    a_vert = np.array([])
    b_vert = np.array([])

    for row in result_matrix:
        k_prime_l_quad = row[0]
        kappa_quad = get_kappa_quad(k_prime_l_quad)
        ff = get_ff(k_prime_l_quad)
        sigma_x = row[1]
        xfer_hor = get_xfer_hor(ff, get_mq_hor(kappa_quad))
        tw_hor = get_twiss_matrix(xfer_hor)
        a_hor = np.append(a_hor, (tw_hor[0, 0], tw_hor[0, 1], tw_hor[0, 2]))
        b_hor = np.append(b_hor, sigma_x ** 2)
    a_hor = np.reshape(a_hor, (nrows, 3))
    X_hor, res_hor, _, _ = np.linalg.lstsq(a_hor, b_hor, rcond=None)
    print()
    print('beta_x * eps_x', X[0])
    print('alhpa_x * eps_x', X[1])
    print('gamma_x * eps_x', X[2])

    # solving a X = b for y-plane
    for row in result_matrix:
        k_prime_l_quad = row[0]
        kappa_quad = get_kappa_quad(k_prime_l_quad)
        ff = get_ff(k_prime_l_quad)
        sigma_y = row[2]
        xfer_vert = get_xfer_vert(ff, get_mq_vert(kappa_quad))
        tw_vert = get_twiss_matrix(xfer_vert)
        a_vert = np.append(
            a_vert, (tw_vert[0, 0], tw_vert[0, 1], tw_vert[0, 2]))
        b_vert = np.append(b_vert, sigma_y ** 2)
    a_vert = np.reshape(a_vert, (nrows, 3))
    X_vert, res_vert, _, _ = np.linalg.lstsq(a_vert, b_vert, rcond=None)
    print()
    print('beta_y * eps_y= ', X[0])
    print('alhpa_y * eps_y= ', X[1])
    print('gamma_y * eps_y= ', X[2])
    return X_hor, res_hor, X_vert, res_vert

# ---------


if __name__ == '__main__':

    # work with some test values

    k_prime_l_quad = calculate_k_prime_l_quad()

    # use the calculated value for the rest of the calculations
    kappa_quad = get_kappa_quad(k_prime_l_quad)
    ff = get_ff(k_prime_l_quad)
    # xplane
    xfer_hor = get_xfer_hor(ff, get_mq_hor(kappa_quad))
    beta = 12.49
    alpha = 7.075
    print('horizontal beta1, alpha1, gamma1', transform(beta, alpha, xfer_hor))
    # y plane
    xfer_vert = get_xfer_vert(ff, get_mq_vert(kappa_quad))
    beta = 115.597
    alpha = -26.909
    print('vertical beta1, alpha1, gamma1', transform(beta, alpha, xfer_vert))
