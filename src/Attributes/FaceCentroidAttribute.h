/* This file is part of PyMesh. Copyright (c) 2015 by Qingnan Zhou */
#pragma once

#include "MeshAttribute.h"

class FaceCentroidAttribute : public MeshAttribute {
    public:
        FaceCentroidAttribute(const std::string& name) : MeshAttribute(name) {}
        virtual ~FaceCentroidAttribute() {}

    public:
        virtual void compute_from_mesh(Mesh& mesh);
};
