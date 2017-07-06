#!/usr/bin/python
# -*- coding: utf-8 -*-
from math import sqrt

import numpy as np


def dcos_plane(attitude):
    """Converts poles into direction cossines."""
    dd, d = np.transpose(np.radians(attitude))  # dip direction, dip
    return np.array((-np.sin(d)*np.sin(dd),
                     -np.sin(d)*np.cos(dd),
                     -np.cos(d))).T


def sphere_plane(data):
    """Calculates the attitude of poles direction cossines."""
    x, y, z = np.transpose(data)
    sign_z = np.where(z > 0, 1, -1)
    z = np.clip(z, -1., 1.)
    return np.array((np.degrees(np.arctan2(sign_z*x, sign_z*y)) % 360,
                     np.degrees(np.arccos(np.abs(z))))).T


def dcos_line(attitude):
    """Converts lines into direction cosines."""
    tr, pl = np.transpose(np.radians(attitude))  # trend, plunge
    return np.array((np.cos(pl)*np.sin(tr),
                    np.cos(pl)*np.cos(tr),
                     -np.sin(pl))).T


def sphere_line(data):
    """Calculate the attitude of lines direction cosines."""
    x, y, z = np.transpose(data)
    sign_z = np.where(z > 0, -1, 1)
    z = np.clip(z, -1., 1.)
    return np.array((np.degrees(np.arctan2(sign_z*x, sign_z*y)) % 360,
                     np.degrees(np.arcsin(np.abs(z))))).T


def project_equal_angle(data, invert_positive=True):
    """Projects a point from the unit sphere to a plane using
    stereographic projection"""
    x, y, z = np.transpose(data)
    if invert_positive:
        c = np.where(z > 0, -1, 1)
        x, y, z = c*x, c*y, c*z
    return x/(1-z), y/(1-z)


def read_equal_angle(data):
    """Inverts the projection of a point from the unit sphere
    to a plane using stereographic projection"""
    X, Y = np.transpose(data)
    x = 2.*X/(1. + X*X + Y*Y)
    y = 2.*Y/(1. + X*X + Y*Y)
    z = (-1. + X*X + Y*Y)/(1. + X*X + Y*Y)
    return x, y, z


def project_equal_area(data, invert_positive=True):
    """Projects a point from the unit sphere to a plane using
    lambert equal-area projection, though shrinking the projected
    sphere radius to 1 from sqrt(2)."""
    x, y, z = np.transpose(data)
    # normalize the data before projection
    d = 1./np.sqrt(x*x + y*y + z*z)
    if invert_positive:
        c = np.where(z > 0, -1, 1)*d
        x, y, z = c*x, c*y, c*z
    else:
        x, y, z = d*x, d*y, d*z
    return x*np.sqrt(1/(1-z)), y*np.sqrt(1/(1-z))


def read_equal_area(data):
    """Inverts the projection of a point from the unit sphere
    to a plane using lambert equal-area projection, cosidering
    that the projected radius of the sphere was shrunk to 1 from
    sqrt(2)."""
    X, Y = np.transpose(data)*sqrt(2)  # Does python optimize this?
    x = np.sqrt(1 - (X*X + Y*Y)/4.)*X
    y = np.sqrt(1 - (X*X + Y*Y)/4.)*Y
    z = -1. + (X*X + Y*Y)/2
    return x, y, z


def normalized_cross(a, b):
    """Returns the normalized cross product between input vectors"""
    c = np.cross(a, b)
    length = sqrt(c.dot(c))
    return c/length if length > 0 else c