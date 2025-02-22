#pragma once

#include <string>

#include <Mesh.h>
#include <MeshFactory.h>
#include <Core/EigenTypedef.h>
#include <Core/Exception.h>
#include <IO/MeshWriter.h>
#include <Misc/Environment.h>
#include <Math/MatrixUtils.h>

/**
 * Base test class.  This class provides some common method often needed during
 * unit testing.
 */
class TestBase : public ::testing::Test {
    protected:
        typedef Mesh::Ptr MeshPtr;

        virtual void SetUp() {
            std::string project_dir = Environment::get("PYMESH_PATH");
            m_data_dir = project_dir + "/tests/data/";
        }

        virtual MeshPtr load_mesh(const std::string& filename) {
            std::string mesh_file = m_data_dir + filename;
            return MeshFactory().load_file(mesh_file).create_shared();
        }

        virtual MeshPtr load_data(
                Eigen::Ref<VectorF> vertices,
                Eigen::Ref<VectorI> faces,
                Eigen::Ref<VectorI> voxels,
                size_t dim, size_t vertex_per_face, size_t vertex_per_voxel) {
            return MeshFactory().load_data(vertices, faces, voxels,
                        dim, vertex_per_face, vertex_per_voxel).create_shared();
        }

        virtual MeshPtr load_data(
                Eigen::Ref<MatrixFr> vertices,
                Eigen::Ref<MatrixIr> faces,
                Eigen::Ref<MatrixIr> voxels) {
            return load_data(
                    MatrixUtils::flatten<VectorF>(vertices),
                    MatrixUtils::flatten<VectorI>(faces),
                    MatrixUtils::flatten<VectorI>(voxels),
                    vertices.cols(), faces.cols(), voxels.cols());
        }

        virtual void write_mesh(const std::string& mesh_file, MeshPtr mesh,
                bool in_ascii=false) {
            MeshWriter::Ptr writer = MeshWriter::create(mesh_file);
            if (in_ascii) writer->in_ascii();
            writer->write_mesh(*mesh);
        }

        virtual void write_mesh_raw(const std::string& mesh_file,
                const Eigen::Ref<const VectorF>& vertices,
                const Eigen::Ref<const VectorI>& faces,
                const Eigen::Ref<const VectorI>& voxels,
                size_t dim, size_t vertex_per_face, size_t vertex_per_voxel,
                bool in_ascii=false) {
            MeshWriter::Ptr writer = MeshWriter::create(mesh_file);
            if (in_ascii) writer->in_ascii();
            writer->write(vertices, faces, voxels,
                    dim, vertex_per_face, vertex_per_voxel);
        }

        virtual void write_mesh_raw(const std::string& mesh_file,
                const Eigen::Ref<const MatrixFr>& vertices,
                const Eigen::Ref<const MatrixIr>& faces,
                const Eigen::Ref<const MatrixIr>& voxels,
                bool in_ascii=false) {
            auto flattened_vertices = MatrixUtils::flatten<VectorF>(vertices);
            auto flattened_faces = MatrixUtils::flatten<VectorI>(faces);
            auto flattened_voxels = MatrixUtils::flatten<VectorI>(voxels);
            write_mesh_raw(mesh_file,
                    flattened_vertices, flattened_faces, flattened_voxels,
                    vertices.cols(), faces.cols(), voxels.cols(), in_ascii);
        }

        virtual void write_mesh_raw(const std::string& mesh_file,
                const Eigen::Ref<const MatrixFr>& vertices,
                const Eigen::Ref<const MatrixIr>& faces,
                bool in_ascii=false) {
            auto flattened_vertices = MatrixUtils::flatten<VectorF>(vertices);
            auto flattened_faces = MatrixUtils::flatten<VectorI>(faces);
            VectorI flattened_voxels = VectorI::Zero(0);
            write_mesh_raw(mesh_file,
                    flattened_vertices, flattened_faces, flattened_voxels,
                    vertices.cols(), faces.cols(), 0, in_ascii);
        }

    protected:
        /**
         * Compare two matrices entry by entry.
         */
        template<typename Derived1, typename Derived2>
        void ASSERT_MATRIX_EQ(
                const Eigen::MatrixBase<Derived1>& M1,
                const Eigen::MatrixBase<Derived2>& M2) {
            ASSERT_FLOAT_EQ(0.0, (M1 - M2).squaredNorm());
        }

    protected:
        std::string m_data_dir;
};
