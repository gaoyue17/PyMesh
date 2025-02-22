/* This file is part of PyMesh. Copyright (c) 2015 by Qingnan Zhou */
#include "WireEdgeSymmetryAttribute.h"

#include <Wires/WireNetwork/WireNetwork.h>
#include <Wires/Misc/SymmetryOperators.h>

namespace WireEdgeSymmetryAttributeHelper {
    using namespace SymmetryOperators;

    Operators get_symmetry_operators(size_t dim, const VectorF& center) {
        if (dim == 2) {
            return generate_reflective_symmetry_operators<2>(center);
        } else if (dim == 3) {
            return generate_reflective_symmetry_operators<3>(center);
        } else {
            throw NotImplementedError(
                    "Symmetry operations only supports 2D and 3D");
        }
    }

    VectorI get_edge_labels(const MatrixFr& vertices, const MatrixIr& edges, Operators& ops) {
        SymmetryConnectivity connectivity =
            compute_edge_connectivity(vertices, edges, ops);
        return label_connected_components(edges.rows(), connectivity);
    }
}
using namespace WireEdgeSymmetryAttributeHelper;

void WireEdgeSymmetryAttribute::compute(const WireNetwork& network) {
    Operators ops = get_symmetry_operators(
            network.get_dim(), network.center());
    VectorI orbit_labels = get_edge_labels(
            network.get_vertices(), network.get_edges(), ops);
    m_values = orbit_labels.cast<Float>();
}
