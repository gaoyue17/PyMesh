%include "std_shared_ptr.i"
%shared_ptr(Material);
%{
#include "Materials/Material.h"
%}
%include "std_vector.i"
namespace std {
    %template(vectors) vector<string>;
};
%include "Materials/Material.h"
