/*
 * module.c — C extension entry point for ttyz.ext.
 *
 * Single compilation unit: includes the split source files and
 * registers all types and functions into the Python module.
 */

#include "core.h"
#include "buffer.c"
#include "text.c"
#include "layout.c"

/* ── Module definition ─────────────────────────────────────────────── */

static PyMethodDef module_methods[] = {
    /* text */
    {"char_width",     mod_char_width,     METH_O,                       "Display width of a single character."},
    {"display_width",  mod_display_width,  METH_O,                       "Display width of a string (ANSI-aware)."},
    {"strip_ansi",     mod_strip_ansi,     METH_O,                       "Remove ANSI escape sequences from string."},
    {"slice_at_width", mod_slice_at_width, METH_VARARGS,                 "Slice plain string to fit display width."},
    {"truncate",       (PyCFunction)mod_truncate, METH_VARARGS | METH_KEYWORDS, "Truncate string to max visible width."},
    /* layout */
    {"place_at_offsets", mod_place_at_offsets, METH_O,      "Place strings at absolute offsets into a line."},
    {"pad_columns",      mod_pad_columns,     METH_VARARGS, "Pad strings to column widths and join with spacing."},
    {"flex_distribute",  mod_flex_distribute,  METH_VARARGS, "Resolve flex column widths from basis + grow."},
    {"distribute",       mod_distribute,       METH_VARARGS, "Distribute total proportionally among weights."},
    {NULL}
};

static struct PyModuleDef module_def = {
    PyModuleDef_HEAD_INIT,
    .m_name    = "ttyz.ext",
    .m_doc     = "C-accelerated terminal rendering primitives.",
    .m_size    = -1,
    .m_methods = module_methods,
};

PyMODINIT_FUNC PyInit_ext(void) {
    if (PyType_Ready(&BufferType) < 0)
        return NULL;
    if (PyType_Ready(&CTextRenderType) < 0)
        return NULL;

    PyObject *m = PyModule_Create(&module_def);
    if (!m) return NULL;

    Py_INCREF(&BufferType);
    if (PyModule_AddObject(m, "Buffer", (PyObject *)&BufferType) < 0) {
        Py_DECREF(&BufferType);
        Py_DECREF(m);
        return NULL;
    }

    Py_INCREF(&CTextRenderType);
    if (PyModule_AddObject(m, "TextRender", (PyObject *)&CTextRenderType) < 0) {
        Py_DECREF(&CTextRenderType);
        Py_DECREF(m);
        return NULL;
    }

    return m;
}
