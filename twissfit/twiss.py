# -*- coding: utf-8 -*-
"""
TWISS parameter calculations

2019

Xaratustrah (S. Sanjari)
based on method / calculations by: H. Weick

Reference:

H. Wollnik, Optics of Charged Particles, Academic Press, 1987, pages 52, 152 and 154,
In the above reference, B, A and C are beta, alpha and gamma Twiss / Courant-Snyder parameters.



"""

import numpy as np
import matplotlib.pyplot as plt

L_DRIFT = 2.216  # m
L_GEO_QUAD = 1  # m
R_QUAD = 0.085  # m
I1A_NORM = 0.00092
BRHO = 8.151048  # Tm
B = -0.23044572  # T


def get_gamma(beta, alpha):
    return (1 + alpha**2) / beta


def get_sigma(beta, eps):
    return np.sqrt(beta * eps)


def calculate_k_prime_l_quad():
    return B * L_GEO_QUAD / R_QUAD / BRHO


def get_drift(ldrift):
    return np.array([[1, ldrift], [0, 1]])


def get_kappa_quad(k_prime_l_quad):
    return np.sqrt(np.abs(k_prime_l_quad / L_GEO_QUAD))


def get_ff(k_prime_l_quad):
    return np.array([[1 - I1A_NORM * k_prime_l_quad / L_GEO_QUAD, 0], [0, 1 + I1A_NORM * k_prime_l_quad / L_GEO_QUAD]])


def get_mq_hor(kappa_quad):
    return np.array([[np.cosh(kappa_quad * L_GEO_QUAD), 1 / kappa_quad * np.sinh(kappa_quad * L_GEO_QUAD)], [kappa_quad * np.sinh(kappa_quad * L_GEO_QUAD), np.cosh(kappa_quad * L_GEO_QUAD)]])


def get_mq_vert(kappa_quad):
    return np.array([[np.cos(kappa_quad * L_GEO_QUAD), 1 / kappa_quad * np.sin(kappa_quad * L_GEO_QUAD)], [-kappa_quad * np.sin(kappa_quad * L_GEO_QUAD), np.cos(kappa_quad * L_GEO_QUAD)]])


def get_xfer_hor(ff, mq_hor, ldrift):
    # (x|x), (x|a)
    # (a|x), (a|a)
    return get_drift(ldrift) @ np.flip(ff).T @ mq_hor @ ff


def get_xfer_vert(ff, mq_vert, ldrift):
    # (y|y), (y|b)
    # (b|y), (b|b)
    return get_drift(ldrift) @ ff @ mq_vert @ np.flip(ff).T


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


def get_epsilon(X):
    return np.sqrt(X[0] * X[2] - X[1]**2)


def plot_sigma_vs_k_prime_l(result_matrix, beta_x, alpha_x, eps_x, beta_y, alpha_y, eps_y):
    k_prime_l_quad_max = result_matrix.max(axis=0)[0] * (1 + 0.1)
    kl_iter = np.linspace(0.01, k_prime_l_quad_max, 200)
    sigma_x_array = np.array([])
    sigma_y_array = np.array([])

    for kl in kl_iter:
        kappa_quad = get_kappa_quad(kl)
        ff = get_ff(kl)
        # x-plane
        xfer_hor = get_xfer_hor(ff, get_mq_hor(kappa_quad), L_DRIFT)
        beta_x_at_l, alpha_x_at_l, _ = transform(beta_x, alpha_x, xfer_hor)
        sigma_x_array = np.append(sigma_x_array, get_sigma(beta_x_at_l, eps_x))

    for kl in kl_iter:
        kappa_quad = get_kappa_quad(kl)
        ff = get_ff(kl)
        # y-plane
        xfer_vert = get_xfer_vert(ff, get_mq_vert(kappa_quad), L_DRIFT)
        beta_y_at_l, alpha_y_at_l, _ = transform(beta_y, alpha_y, xfer_vert)
        sigma_y_array = np.append(sigma_y_array, get_sigma(beta_y_at_l, eps_y))

    fig = plt.figure()
    ax = fig.gca()
    ax.plot(kl_iter, sigma_x_array, label='sigma_x')
    ax.plot(kl_iter, sigma_y_array, label='sigma_y')
    # ax.plot(result_matrix[0], result_matrix[1],
    #         'rs', label='sigma_x data')
    # ax.plot(result_matrix[0], result_matrix[2],
    #         'bs', label='sigma_y data')
    print(result_matrix)
    ax.set_xlabel("K'L")
    ax.set_ylabel("sigma [mm]")
    ax.set_title("Sigma vs. K'L @ {} m from ref. plane".format(L_DRIFT))
    # Now add the legend with some customizations.
    legend = ax.legend(loc='upper right', shadow=False)

    # Set legend fontsize
    for label in legend.get_texts():
        label.set_fontsize('small')

    ax.grid(True)
    plt.savefig('sigma_K_L_at_{}.pdf'.format(L_DRIFT))


def plot_sigma_vs_distance(result_matrix, beta_x, alpha_x, eps_x, beta_y, alpha_y, eps_y):
    # choose the first of the K'L that the user had input
    kl = result_matrix[0, 0]
    sigma_x_array = np.array([])
    sigma_y_array = np.array([])

    l_iter = np.arange(0.1, 5, 0.1)  # every 10 centemeters
    for ll in l_iter:
        kappa_quad = get_kappa_quad(kl)
        ff = get_ff(kl)
        # x-plane
        xfer_hor = get_xfer_hor(ff, get_mq_hor(kappa_quad), ll)
        beta_x_at_l, alpha_x_at_l, _ = transform(beta_x, alpha_x, xfer_hor)
        sigma_x_array = np.append(sigma_x_array, get_sigma(beta_x_at_l, eps_x))

    for ll in l_iter:
        kappa_quad = get_kappa_quad(kl)
        ff = get_ff(kl)
        # y-plane
        xfer_vert = get_xfer_vert(ff, get_mq_vert(kappa_quad), ll)
        beta_y_at_l, alpha_y_at_l, _ = transform(beta_y, alpha_y, xfer_vert)
        sigma_y_array = np.append(sigma_y_array, get_sigma(beta_y_at_l, eps_y))

    fig = plt.figure()
    ax = fig.gca()
    ax.plot(l_iter, sigma_x_array, label='sigma_x')
    ax.plot(l_iter, sigma_y_array, label='sigma_y')
    ax.set_xlabel("Distance [m]")
    ax.set_ylabel("sigma [mm]")
    ax.set_title("Sigma vs. Distance for K'L = {}".format(kl))
    # Now add the legend with some customizations.
    legend = ax.legend(loc='upper right', shadow=False)

    # Set legend fontsize
    for label in legend.get_texts():
        label.set_fontsize('small')

    ax.grid(True)
    plt.savefig('sigma_distance_at_K_L_{}.pdf'.format(kl))

# ------


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
        xfer_hor = get_xfer_hor(ff, get_mq_hor(kappa_quad), L_DRIFT)
        tw_hor = get_twiss_matrix(xfer_hor)
        a_hor = np.append(a_hor, (tw_hor[0, 0], tw_hor[0, 1], tw_hor[0, 2]))
        b_hor = np.append(b_hor, sigma_x ** 2)
    a_hor = np.reshape(a_hor, (nrows, 3))
    X_hor, res_hor, _, _ = np.linalg.lstsq(a_hor, b_hor, rcond=None)

    beta_x = X_hor[0] / get_epsilon(X_hor)
    alpha_x = X_hor[1] / get_epsilon(X_hor)
    gamma_x = X_hor[2] / get_epsilon(X_hor)
    eps_x = get_epsilon(X_hor)

    print()
    print('beta_x = ', beta_x)
    print('alpha_x = ', alpha_x)
    print('gamma_x = ', gamma_x)
    print('eps_x = ', eps_x)

    # solving a X = b for y-plane
    for row in result_matrix:
        k_prime_l_quad = row[0]
        kappa_quad = get_kappa_quad(k_prime_l_quad)
        ff = get_ff(k_prime_l_quad)
        sigma_y = row[2]
        xfer_vert = get_xfer_vert(ff, get_mq_vert(kappa_quad), L_DRIFT)
        tw_vert = get_twiss_matrix(xfer_vert)
        a_vert = np.append(
            a_vert, (tw_vert[0, 0], tw_vert[0, 1], tw_vert[0, 2]))
        b_vert = np.append(b_vert, sigma_y ** 2)
    a_vert = np.reshape(a_vert, (nrows, 3))
    X_vert, res_vert, _, _ = np.linalg.lstsq(a_vert, b_vert, rcond=None)

    beta_y = X_vert[0] / get_epsilon(X_vert)
    alpha_y = X_vert[1] / get_epsilon(X_vert)
    gamma_y = X_vert[2] / get_epsilon(X_vert)
    eps_y = get_epsilon(X_vert)

    print()
    print('beta_y = ', beta_y)
    print('alpha_y = ', alpha_y)
    print('gamma_y = ', gamma_y)
    print('eps_y = ', eps_y)
    return beta_x, alpha_x, eps_x, beta_y, alpha_y, eps_y

# ---------


if __name__ == '__main__':

    # work with some test values

    k_prime_l_quad = calculate_k_prime_l_quad()

    # use the calculated value for the rest of the calculations
    kappa_quad = get_kappa_quad(k_prime_l_quad)
    ff = get_ff(k_prime_l_quad)
    # xplane
    xfer_hor = get_xfer_hor(ff, get_mq_hor(kappa_quad), L_DRIFT)
    beta = 12.49
    alpha = 7.075
    print('horizontal beta1, alpha1, gamma1', transform(beta, alpha, xfer_hor))
    # y plane
    xfer_vert = get_xfer_vert(ff, get_mq_vert(kappa_quad), L_DRIFT)
    beta = 115.597
    alpha = -26.909
    print('vertical beta1, alpha1, gamma1', transform(beta, alpha, xfer_vert))
