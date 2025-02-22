/* This file is part of PyMesh. Copyright (c) 2015 by Qingnan Zhou */
#pragma once
#include <string>

namespace IOUtils {
    std::string get_extention(const std::string& filename);
    bool is_prefix(const char* prefix, const char* str);
}
