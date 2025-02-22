/* This file is part of PyMesh. Copyright (c) 2015 by Qingnan Zhou */
#pragma once

#include <Boolean/BooleanEngine.h>

class CGALBooleanEngine : public BooleanEngine {
    public:
        virtual ~CGALBooleanEngine() {}

    public:
        virtual void compute_union();
        virtual void compute_intersection();
        virtual void compute_difference();
        virtual void compute_symmetric_difference();
};
