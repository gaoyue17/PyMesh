#!/usr/bin/env python
# This file is part of PyMesh. Copyright (c) 2015 by Qingnan Zhou #

import numpy as np
import os
import os.path
import scipy.sparse
from scipy.io import loadmat
import sys
import unittest

PYMESH_PATH = os.environ.get("PYMESH_PATH");
if PYMESH_PATH is None:
    raise ImportError("Please set PYMESH_PATH to the correct lib path.")
sys.path.append(os.path.join(PYMESH_PATH, "lib"));
sys.path.append(os.path.join(PYMESH_PATH, "swig"));

import PyMesh
import PyAssembler

class FEAssemblerTest(unittest.TestCase):
    def setUp(self):
        self.data_dir = os.path.join(PYMESH_PATH, "tests/data/");
        self.ground_truth_dir = os.path.join(PYMESH_PATH,
                "tests/tools/Assembler/ground_truth/");
        self.material_name = "test_material";

    def load_mesh(self, mesh_file):
        mesh_file = os.path.join(self.data_dir, mesh_file);
        if not os.path.exists(mesh_file):
            raise IOError("mesh file {} does not exist!".format(mesh_file));

        factory = PyMesh.MeshFactory();
        factory.load_file(mesh_file);
        factory.with_connectivity("all");
        factory.with_attribute("face_normal");
        factory.with_attribute("vertex_normal");
        factory.with_attribute("face_area");
        factory.with_attribute("voxel_volume");
        return factory.create_shared();

    def create_assembler(self, mesh):
        return PyAssembler.FEAssembler.create_from_name(mesh, self.material_name);

    def create_assembler_from_material(self, mesh):
        material = PyAssembler.Material.create_isotropic(
                mesh.get_dim(), 1.0, 1.0, 0.0);
        return PyAssembler.FEAssembler.create(mesh, material);

    def load_matrix(self, filename, matrix_name):
        filename = os.path.join(self.ground_truth_dir, filename);
        matrix = loadmat(filename)[matrix_name];
        return matrix;

    def format(self, matrix):
        return matrix;

    def assertMatrixEqual(self, M1, M2):
        diff = M1 - M2;
        if diff.nnz > 0:
            self.assertAlmostEqual(0.0, np.max(diff.data));
            self.assertAlmostEqual(0.0, np.min(diff.data));

    def test_creation(self):
        mesh = self.load_mesh("tet.msh");
        assembler_1 = self.create_assembler(mesh);
        assembler_2 = self.create_assembler_from_material(mesh);
        K1 = self.format(assembler_1.assemble("stiffness"));
        K2 = self.format(assembler_2.assemble("stiffness"));
        self.assertMatrixEqual(K1, K2);

    def test_stiffness_tet(self):
        mesh = self.load_mesh("tet.msh");
        assembler = self.create_assembler(mesh);
        K = self.format(assembler.assemble("stiffness"));
        K_ground_truth = self.load_matrix("tet_stiffness.mat", "K");
        self.assertMatrixEqual(K_ground_truth, K);

    def test_stiffness_square(self):
        mesh = self.load_mesh("square_2D.obj");
        assembler = self.create_assembler(mesh);
        K = self.format(assembler.assemble("stiffness"));
        K_ground_truth = self.load_matrix("square_2D_stiffness.mat", "K");
        self.assertMatrixEqual(K_ground_truth, K);

    def test_stiffness_decomposition_tet(self):
        mesh = self.load_mesh("tet.msh");
        assembler = self.create_assembler(mesh);
        K = self.format(assembler.assemble("stiffness"));
        B = self.format(assembler.assemble("displacement_strain"));
        D = self.format(assembler.assemble("elasticity_tensor"));
        dia_entries = np.ones(D.shape[0]);
        for i in range(3, D.shape[0], 6):
            dia_entries[i] = 2.0;
            dia_entries[i+1] = 2.0;
            dia_entries[i+2] = 2.0;
        C = scipy.sparse.diags(dia_entries, 0);
        areas = mesh.get_attribute("voxel_volume").ravel();
        A = scipy.sparse.diags(np.repeat(areas, 6), 0);
        self.assertMatrixEqual(K, B.T*A*C*D*B);

    def test_stiffness_decomposition_square(self):
        mesh = self.load_mesh("square_2D.obj");
        assembler = self.create_assembler(mesh);
        K = self.format(assembler.assemble("stiffness"));
        B = self.format(assembler.assemble("displacement_strain"));
        D = self.format(assembler.assemble("elasticity_tensor"));
        dia_entries = np.ones(D.shape[0]);
        for i in range(2, D.shape[0], 3):
            dia_entries[i] = 2.0;
        C = scipy.sparse.diags(dia_entries, 0);
        areas = mesh.get_attribute("face_area").ravel();
        A = scipy.sparse.diags(np.repeat(areas, 3), 0);
        self.assertMatrixEqual(K, B.T*A*C*D*B);

    def test_mass_tet(self):
        mesh = self.load_mesh("tet.msh");
        assembler = self.create_assembler(mesh);
        M = self.format(assembler.assemble("mass"));
        M_ground_truth = self.load_matrix("tet_mass.mat", "M");
        self.assertMatrixEqual(M_ground_truth, M);

    def test_mass_square(self):
        mesh = self.load_mesh("square_2D.obj");
        assembler = self.create_assembler(mesh);
        M = self.format(assembler.assemble("mass"));
        M_ground_truth = self.load_matrix("square_2D_mass.mat", "M");
        self.assertMatrixEqual(M_ground_truth, M);

    def test_lumped_mass_tet(self):
        mesh = self.load_mesh("tet.msh");
        assembler = self.create_assembler(mesh);
        M = self.format(assembler.assemble("lumped_mass"));
        M_ground_truth = self.load_matrix("tet_lumped_mass.mat", "M");
        self.assertMatrixEqual(M_ground_truth, M);

    def test_lumped_mass_square(self):
        mesh = self.load_mesh("square_2D.obj");
        assembler = self.create_assembler(mesh);
        M = self.format(assembler.assemble("lumped_mass"));
        M_ground_truth = self.load_matrix("square_2D_lumped_mass.mat", "M");
        self.assertMatrixEqual(M_ground_truth, M);

    def test_laplacian_tet(self):
        mesh = self.load_mesh("tet.msh");
        assembler = self.create_assembler(mesh);
        L = self.format(assembler.assemble("laplacian"));
        L_ground_truth = self.load_matrix("tet_laplacian.mat", "L");
        self.assertMatrixEqual(L_ground_truth, L);

    def test_laplaican_square(self):
        mesh = self.load_mesh("square_2D.obj");
        assembler = self.create_assembler(mesh);
        L = self.format(assembler.assemble("laplacian"));
        L_ground_truth = self.load_matrix("square_2D_laplacian.mat", "L");
        self.assertMatrixEqual(L_ground_truth, L);

    def test_displacement_strain_tet(self):
        mesh = self.load_mesh("tet.msh");
        assembler = self.create_assembler(mesh);
        B = self.format(assembler.assemble("displacement_strain"));
        B_ground_truth = self.load_matrix("tet_displacement_strain.mat", "B");
        self.assertMatrixEqual(B_ground_truth, B);

    def test_displacement_strain_square(self):
        mesh = self.load_mesh("square_2D.obj");
        assembler = self.create_assembler(mesh);
        B = self.format(assembler.assemble("displacement_strain"));
        B_ground_truth = self.load_matrix("square_2D_displacement_strain.mat", "B");
        self.assertMatrixEqual(B_ground_truth, B);

    def test_elasticity_tensor_tet(self):
        mesh = self.load_mesh("tet.msh");
        assembler = self.create_assembler(mesh);
        C = self.format(assembler.assemble("elasticity_tensor"));
        C_ground_truth = self.load_matrix("tet_elasticity_tensor.mat", "C");
        self.assertMatrixEqual(C_ground_truth, C);

    def test_elasticity_tensor_square(self):
        mesh = self.load_mesh("square_2D.obj");
        assembler = self.create_assembler(mesh);
        C = self.format(assembler.assemble("elasticity_tensor"));
        C_ground_truth = self.load_matrix("square_2D_elasticity_tensor.mat", "C");
        self.assertMatrixEqual(C_ground_truth, C);

    def test_engineer_strain_stress_tet(self):
        mesh = self.load_mesh("tet.msh");
        assembler = self.create_assembler(mesh);
        C  = self.format(assembler.assemble("elasticity_tensor"));
        Ce = self.format(assembler.assemble("engineer_strain_stress"));
        doubler_diag = np.tile([1.0, 1.0, 1.0, 2.0, 2.0, 2.0],
                mesh.get_num_voxels());
        doubler = scipy.sparse.diags(doubler_diag, 0);
        self.assertMatrixEqual(doubler * C, Ce);

    def test_engineer_strain_stress_square(self):
        mesh = self.load_mesh("square_2D.obj");
        assembler = self.create_assembler(mesh);
        C  = self.format(assembler.assemble("elasticity_tensor"));
        Ce = self.format(assembler.assemble("engineer_strain_stress"));
        doubler_diag = np.tile([1.0, 1.0, 2.0], mesh.get_num_faces());
        doubler = scipy.sparse.diags(doubler_diag, 0);
        self.assertMatrixEqual(doubler * C, Ce);

    def test_rigid_motion_under_stretch_tet(self):
        mesh = self.load_mesh("tet.msh");
        mesh.add_attribute("vertex_volume");
        assembler = self.create_assembler(mesh);
        Ru = self.format(assembler.assemble("rigid_motion"));

        dim = mesh.get_dim();
        num_vertices = mesh.get_num_vertices();
        vertices = mesh.get_vertices().reshape((num_vertices, -1));
        vertex_volumes = mesh.get_attribute("vertex_volume").ravel();
        center_of_mass = np.average(vertices, axis=0, weights=vertex_volumes);
        uniform_stretch = (vertices - center_of_mass).ravel(order="C");

        rigid_motion = (Ru * uniform_stretch).ravel();
        self.assertAlmostEqual(0.0, np.amax(rigid_motion));
        self.assertAlmostEqual(0.0, np.amin(rigid_motion));

    def test_rigid_motion_under_uniform_stretch_square(self):
        mesh = self.load_mesh("square_2D.obj");
        mesh.add_attribute("vertex_area");
        assembler = self.create_assembler(mesh);
        Ru = self.format(assembler.assemble("rigid_motion"));

        dim = mesh.get_dim();
        num_vertices = mesh.get_num_vertices();
        vertices = mesh.get_vertices().reshape((num_vertices, -1));
        vertex_areas = mesh.get_attribute("vertex_area").ravel();
        center_of_mass = np.average(vertices, axis=0, weights=vertex_areas);
        uniform_stretch = (vertices - center_of_mass).ravel(order="C");

        rigid_motion = (Ru * uniform_stretch).ravel();
        self.assertAlmostEqual(0.0, np.amax(rigid_motion));
        self.assertAlmostEqual(0.0, np.amin(rigid_motion));

    def test_rigid_motion_in_stiffness_null_space(self):
        mesh = self.load_mesh("square_2D.obj");
        assembler = self.create_assembler(mesh);
        Ru = self.format(assembler.assemble("rigid_motion"));
        K = self.format(assembler.assemble("stiffness"));

        result = K * Ru.T;
        self.assertAlmostEqual(0.0, result.min());
        self.assertAlmostEqual(0.0, result.max());
