# This file is part of PyMesh. Copyright (c) 2015 by Qingnan Zhou #
import numpy as np
import os.path
import unittest

from PyMeshSetting import PYMESH_PATH
import PyMesh
import PyMeshUtils

class IsolatedVertexRemovalTest(unittest.TestCase):
    def setUp(self):
        self.data_dir = os.path.join(PYMESH_PATH, "tests/data/");
        self.tol = 1e-3;

    def load_mesh(self, mesh_file):
        mesh_file = os.path.join(self.data_dir, mesh_file);
        if not os.path.exists(mesh_file):
            raise IOError("mesh file {} does not exist!".format(mesh_file));

        factory = PyMesh.MeshFactory();
        factory.load_file(mesh_file);
        return factory.create();

    def assert_matrix_eq(self, m1, m2):
        diff = m1 - m2;
        self.assertAlmostEqual(0.0, np.amax(diff));
        self.assertAlmostEqual(0.0, np.amin(diff));

    def get_raw_data(self, mesh):
        dim = mesh.get_dim();
        num_vertices = mesh.get_num_vertices();
        num_faces = mesh.get_num_faces();
        vertex_per_face = mesh.get_vertex_per_face();
        vertices = mesh.get_vertices().reshape((num_vertices, dim), order="C");
        faces = mesh.get_faces().reshape((num_faces, vertex_per_face), order="C");

        return vertices, faces;

    def add_extra_vertex(self, vertices, faces):
        dim = vertices.shape[1];
        modified_vertices = np.vstack((np.ones(dim), vertices));
        modified_faces = faces + 1;

        return modified_vertices, modified_faces;

    def run_remover(self, vertices, faces):
        remover = PyMeshUtils.IsolatedVertexRemoval(vertices, faces);
        remover.run();
        result_vertices = remover.get_vertices();
        result_faces = remover.get_faces();

        # Results should be vaid after remover object is deleted.
        return result_vertices, result_faces;

    def add_extra_vertex_and_check(self, mesh):
        ori_vertices, ori_faces = self.get_raw_data(mesh);
        modified_vertices, modified_faces = self.add_extra_vertex(
                ori_vertices, ori_faces);
        result_vertices, result_faces = self.run_remover(
                modified_vertices, modified_faces);

        self.assert_matrix_eq(ori_vertices, result_vertices);
        self.assert_matrix_eq(ori_faces, result_faces);

    def test_2D(self):
        mesh = self.load_mesh("square_2D.obj");
        self.add_extra_vertex_and_check(mesh);

    def test_3D(self):
        mesh = self.load_mesh("cube.msh");
        self.add_extra_vertex_and_check(mesh);

