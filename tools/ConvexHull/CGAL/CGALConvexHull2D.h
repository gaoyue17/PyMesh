/* This file is part of PyMesh. Copyright (c) 2015 by Qingnan Zhou */
#pragma once

#include "CGALConvexHull.h"

class CGALConvexHull2D : public CGALConvexHull {
    public:
        virtual void run(const MatrixFr& points);
};
