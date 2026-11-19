from typing import Dict, Tuple, Type, Any


# type_name: (gdb_c_type, printf_format, printf_cast, python_type)
MEMORY_TYPES: Dict[str, Tuple[str, str, str, Type[Any]]] = {

    "uchar":    ( "unsigned char",      "%d",       "(int)",          int   ),
    "schar":    ( "signed char",        "%d",       "(int)",          int   ),
    "ushort":   ( "unsigned short",     "%u",       "(unsigned int)", int   ),
    "short":    ( "short",              "%d",       "(int)",          int   ),
    "uint":     ( "unsigned int",       "%u",       "",               int   ),
    "int":      ( "int",                "%d",       "",               int   ),
    "ulong":    ( "unsigned long",      "%lu",      "",               int   ),
    "long":     ( "long",               "%ld",      "",               int   ),
    "float":    ( "float",              "%.6g",     "(double)",       float ),
    "double":   ( "double",             "%.15g",    "",               float )
    
}
