/* This file is part of PyMesh. Copyright (c) 2016 by Qingnan Zhou */
#pragma once

#include "MeshAttribute.h"

class FaceIncircleRadiusAttribute : public MeshAttribute {
    public:
        FaceIncircleRadiusAttribute(const std::string& name) : MeshAttribute(name) {}
        virtual ~FaceIncircleRadiusAttribute() {}

    public:
        virtual void compute_from_mesh(Mesh& mesh);
};
