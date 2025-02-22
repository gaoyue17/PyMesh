/* This file is part of PyMesh. Copyright (c) 2015 by Qingnan Zhou */
#include "BilinearInterpolation.h"

#include <sstream>
#include <Core/Exception.h>

// Shape functions ordered according to quad vertex order:
//
//  3 +---+ 2
//    |   |
//  0 +---+ 1
//
const BilinearInterpolation::Functions BilinearInterpolation::m_shape_functions = {
    [](const Vector2F& v) { return (1.0 - v[0])*(1.0 - v[1]); },
    [](const Vector2F& v) { return (      v[0])*(1.0 - v[1]); },
    [](const Vector2F& v) { return (      v[0])*(      v[1]); },
    [](const Vector2F& v) { return (1.0 - v[0])*(      v[1]); }
};

BilinearInterpolation::BilinearInterpolation(const MatrixFr& control_pts) : Interpolation(control_pts) {
    const size_t dim = m_control_pts.cols();
    const size_t num_pts = m_control_pts.rows();

    if (dim != 2) {
        std::stringstream err_msg;
        err_msg << "Invalid dim: " << dim
            << ", bilinear interpolation requires dim=2";
        throw RuntimeError(err_msg.str());
    }

    if (num_pts != 4) {
        std::stringstream err_msg;
        err_msg << "Given " << num_pts << " control points.  "
            << "Bilinear interpolation requires 4 control points.";
        throw RuntimeError(err_msg.str());
    }
}

VectorF BilinearInterpolation::interpolate(const VectorF& p) const {
    VectorF bilinear_coordinates(4);
    bilinear_coordinates << 
        m_shape_functions[0](p),
        m_shape_functions[1](p),
        m_shape_functions[2](p),
        m_shape_functions[3](p);
    return (m_control_pts.transpose() * bilinear_coordinates).transpose();
}

MatrixFr BilinearInterpolation::interpolate_batch(const MatrixFr& pts) const {
    const size_t num_pts = pts.rows();
    MatrixFr bilinear_coordinates(num_pts, 4);
    for (size_t i=0; i<num_pts; i++) {
        const VectorF& p = pts.row(i);
        bilinear_coordinates.row(i) << 
            m_shape_functions[0](p),
            m_shape_functions[1](p),
            m_shape_functions[2](p),
            m_shape_functions[3](p);
    }

    return bilinear_coordinates * m_control_pts;
}

