#define PY_ARRAY_UNIQUE_SYMBOL PyArrayHandle
#include <boost/python/numeric.hpp>
#include <boost/python/tuple.hpp>
#include <boost/python/scope.hpp>
#include <boost/python/module.hpp>
#include <boost/python/def.hpp>
#include <num_util.h>
#include <bitset>
#include <iostream>

namespace { const std::string rcsid = ("@(#) $Id: bright.C,v 1.2 2003/03/04 21:59:32 cleung Exp $:"); };

namespace py = boost::python;
namespace nbpl = num_util;

/**
 *Subroutine for parsing MODIS 8-bit cloud mask data.
 *@param an numeric array containing the cloud mask data
 *@return a 6xT numeric array, where T=(scanlines*pixels). Each row contains values for an individual masked variable. Obviously, user is required to resize each row back to its original shape in Python.
 */

/*
+------+------------------------------+------------------------+
| bits |       Field Description      | Bit Interpretation Key |
+------+------------------------------+------------------------+
| 1    | Cloud Mask Flag              | 0 = Not Determined     |
|      |                              | 1 = Determined         |
| 2-3  | Unobstructed FOV Quality Flag| 0 = Cloud              | 
|      |                              | 1 = 66% prob. Clear    |
|      |                              | 2 = 95% prob. Clear    |
|      |                              | 3 = 99% prob. Clear    | 
| 4    | Day/Night Flag               | 0 = Night              |
|      |                              | 1 = Day                | 
| 5    | Sunglint Flag                | 0 = Yes                |
|      |                              | 1 = No                 |
| 6    | Snow/Ice Background Flag     | 0 = Yes                |
|      |                              | 1 = No                 |
| 7-8  | Land/Water Background Flag   | 0=Water                |
|      |                              | 1=Coastal              |
|      |                              | 2=Desert               |
|      |                              | 3=Land                 |
+------+------------------------------+------------------------+
*/
py::numeric::array cloud_mask(py::numeric::array arr){
  int arr_size = nbpl::size(arr);
  std::vector<int> dims;
  dims.push_back(arr_size);
  dims.push_back(6);

  boost::shared_ptr<char> sdata(new char[arr_size*6]);
  char* data = sdata.get();
  char* arr_val = (char*) nbpl::data(arr);
  for(int i = 0; i < arr_size; i++){
    int j = i*6;
    std::bitset<8> myseq(arr_val[i]);
    data[j] = myseq[0];
    data[j+1] = (myseq[1]*1)+(myseq[2]*2);
    data[j+2] = myseq[3];
    data[j+3] = myseq[4];
    data[j+4] = myseq[5];
    data[j+5] = (myseq[6]*1)+(myseq[7]*2);
  }   
  return nbpl::makeNum(data, dims);
}

BOOST_PYTHON_MODULE(bitmap_ext)
{
  using namespace boost::python;
  import_array();
  numeric::array::set_module_and_type("Numeric", "ArrayType");

  scope().attr("RCSID") = rcsid;
  def("cloud_mask", cloud_mask);
}
