/* This file is part of PyMesh. Copyright (c) 2015 by Qingnan Zhou */
#include "IGLEngine.h"

#include <igl/copyleft/cgal/mesh_boolean.h>

namespace IGLEngineHelper {
    void exact_to_float(const IGLEngine::MatrixEr& m_e, MatrixFr& m_f) {
        m_f.resize(m_e.rows(), m_e.cols());
        std::transform(m_e.data(), m_e.data() + m_e.size(),
                m_f.data(), [](const IGLEngine::MatrixEr::Scalar& val)
                { return CGAL::to_double(val); });
    }
}
using namespace IGLEngineHelper;

#ifdef WITH_TINYXML2
#include <tinyxml2.h>
#include <igl/serialize.h>
#include <igl/xml/serialize_xml.h>

// The following is based on http://www.alecjacobson.com/weblog/?p=4477
namespace igl {
namespace xml {
namespace serialization_xml {
    template <> inline void serialize(
            const IGLEngine::MatrixEr & obj,
            tinyxml2::XMLDocument* doc,
            tinyxml2::XMLElement* element,
            const std::string& name) {
        const std::function<std::string(
                const IGLEngine::MatrixEr::Scalar &) > to_string = 
            [](const IGLEngine::MatrixEr::Scalar & v)->std::string {
                return STR(CGAL::exact(v));
            };
        serialize(obj,name,to_string,doc,element);
    }

    template <> inline void deserialize(
            IGLEngine::MatrixEr & obj,
            const tinyxml2::XMLDocument* doc,
            const tinyxml2::XMLElement* element,
            const std::string& name) {
        const std::function<void(const std::string &,
                IGLEngine::MatrixEr::Scalar &)> & 
            from_string = [](
                    const std::string & s, IGLEngine::MatrixEr::Scalar & v) {
                std::stringstream(s)>>v;
            };
        deserialize(doc,element,name,from_string,obj);
    }
}
}
}
#endif

void IGLEngine::compute_union() {
    igl::copyleft::cgal::mesh_boolean(
            m_vertices_1, m_faces_1, 
            m_vertices_2, m_faces_2,
            igl::MESH_BOOLEAN_TYPE_UNION,
            m_exact_vertices, m_faces, m_face_sources);
    exact_to_float(m_exact_vertices, m_vertices);
}

void IGLEngine::compute_intersection() {
    igl::copyleft::cgal::mesh_boolean(
            m_vertices_1, m_faces_1, 
            m_vertices_2, m_faces_2,
            igl::MESH_BOOLEAN_TYPE_INTERSECT,
            m_exact_vertices, m_faces, m_face_sources);
    exact_to_float(m_exact_vertices, m_vertices);
}

void IGLEngine::compute_difference() {
    igl::copyleft::cgal::mesh_boolean(
            m_vertices_1, m_faces_1, 
            m_vertices_2, m_faces_2,
            igl::MESH_BOOLEAN_TYPE_MINUS,
            m_exact_vertices, m_faces, m_face_sources);
    exact_to_float(m_exact_vertices, m_vertices);
}

void IGLEngine::compute_symmetric_difference() {
    igl::copyleft::cgal::mesh_boolean(
            m_vertices_1, m_faces_1, 
            m_vertices_2, m_faces_2,
            igl::MESH_BOOLEAN_TYPE_XOR,
            m_exact_vertices, m_faces, m_face_sources);
    exact_to_float(m_exact_vertices, m_vertices);
}

void IGLEngine::serialize_xml(const std::string& filename) const {
#ifdef WITH_TINYXML2
    // The following code is based on
    // http://www.alecjacobson.com/weblog/?p=4477

    const bool binary = false;
    // Write vertices, overwriting file (true)
    igl::xml::serialize_xml(m_exact_vertices, "vertices", filename, binary, true);
    // Write faces to same file, appending (false)
    igl::xml::serialize_xml(m_faces, "faces", filename, binary, false);
#else
    BooleanEngine::serialize_xml(filename);
#endif
}
