/*
 * types.c — Python type loading + slot-offset discovery.
 *
 * Runs once on first render_to_buffer() call.  Loads node type objects
 * from the Python ttyz.components.* modules, interns constants, and
 * discovers the in-memory offsets of __slots__ attributes so the hot
 * path can bypass the descriptor protocol.
 */

static int render_types_ready = 0;  /* safe: only mutated under the GIL */

/* ── Node type pointers — resolved once from Python classes ───────── */

static PyTypeObject *NodeType_;
static PyTypeObject *TextType_;
static PyTypeObject *HStackType_;
static PyTypeObject *VStackType_;
static PyTypeObject *ZStackType_;
static PyTypeObject *BoxType_;
static PyTypeObject *SpacerType_;
static PyTypeObject *CondType_;
static PyTypeObject *ForeachType_;
static PyTypeObject *ScrollType_;
static PyTypeObject *ScrollbarType_;
static PyTypeObject *TableType_;
static PyTypeObject *TableRowType_;
static PyTypeObject *ScrollStateType_;
static PyTypeObject *InputType_;

/* ── Interned strings ─────────────────────────────────────────────── */

/* Attribute names still read via PyObject_GetAttr (non-slot fields). */
static PyObject *a_value;
static PyObject *a_render_fn;

/* Constants compared by pointer identity after interning. */
static PyObject *s_visible;
static PyObject *s_start;
static PyObject *s_end;
static PyObject *s_center;
static PyObject *s_between;
static PyObject *s_rounded;
static PyObject *s_normal;
static PyObject *s_double;
static PyObject *s_heavy;

/* ── Slot offsets (discovered at init time) ────────────────────────── */
/*
 * CPython stores __slots__ values at fixed offsets inside instances.
 * We discover the offsets once from the member descriptors, then read
 * slot values directly, bypassing the descriptor protocol entirely.
 * This eliminates the dominant per-node cost: PyObject_GetAttr calls
 * that perform MRO lookup + descriptor __get__ on every access.
 */

/* Node base (same offset for every subclass). */
static Py_ssize_t off_children, off_grow, off_width, off_height,
                   off_bg, off_overflow;
/* Text */
static Py_ssize_t off_text_value, off_text_lines, off_text_visible_w,
                   off_text_pl, off_text_pr, off_text_truncation,
                   off_text_wrap;
/* HStack */
static Py_ssize_t off_hstack_spacing, off_hstack_jc, off_hstack_ai,
                   off_hstack_wrap;
/* VStack */
static Py_ssize_t off_vstack_spacing, off_vstack_needs_measure_pass;
/* ZStack */
static Py_ssize_t off_zstack_jc, off_zstack_ai;
/* Box */
static Py_ssize_t off_box_style, off_box_title, off_box_padding;
/* Scroll */
static Py_ssize_t off_scroll_state;
/* Table */
static Py_ssize_t off_table_rows, off_table_spacing;
/* TableRow */
static Py_ssize_t off_trow_cells;
/* ScrollState */
static Py_ssize_t off_ss_offset, off_ss_height, off_ss_total, off_ss_follow;
/* Spacer */
static Py_ssize_t off_spacer_min_length;
/* Input */
static Py_ssize_t off_input_buffer, off_input_active, off_input_placeholder;
/* Scrollbar */
static Py_ssize_t off_scrollbar_state, off_scrollbar_render_fn;

/* Python helpers for Input rendering (imported from Python). */
static PyObject *py_display_text;
static PyObject *py_display_cursor;

/* ── discover_slot_offset / load_type ─────────────────────────────── */

/*
 * Discover the memory offset of a __slots__ attribute on a type.
 * Walks the MRO to find the member_descriptor, then reads its offset.
 * Returns -1 on failure (sets a Python exception).
 */
static Py_ssize_t discover_slot_offset(PyTypeObject *tp, const char *name) {
    PyObject *key = PyUnicode_InternFromString(name);
    if (!key) return -1;
    PyObject *mro = tp->tp_mro;
    Py_ssize_t n = PyTuple_GET_SIZE(mro);
    for (Py_ssize_t i = 0; i < n; i++) {
        PyTypeObject *base = (PyTypeObject *)PyTuple_GET_ITEM(mro, i);
        if (!base->tp_dict) continue;
        PyObject *descr = PyDict_GetItem(base->tp_dict, key); /* borrowed */
        if (descr && Py_TYPE(descr) == &PyMemberDescr_Type) {
            Py_DECREF(key);
            return ((PyMemberDescrObject *)descr)->d_member->offset;
        }
    }
    PyErr_Format(PyExc_RuntimeError,
                 "ttyz: slot '%s' not found on type '%s'",
                 name, tp->tp_name);
    Py_DECREF(key);
    return -1;
}

static PyTypeObject *load_type(const char *module, const char *name) {
    PyObject *mod = PyImport_ImportModule(module);
    if (!mod) return NULL;
    PyObject *cls = PyObject_GetAttrString(mod, name);
    Py_DECREF(mod);
    if (!cls) return NULL;
    return (PyTypeObject *)cls;  /* owns ref */
}

/* ── init_render_types — lazy one-time setup ──────────────────────── */

static int init_render_types(void) {
    if (render_types_ready) return 0;

#define LOAD(var, mod, name) do {            \
    var = load_type(mod, name);              \
    if (!var) return -1;                     \
} while (0)

    LOAD(NodeType_,        "ttyz.components.base",      "Node");
    LOAD(TextType_,        "ttyz.components.text",      "Text");
    LOAD(HStackType_,      "ttyz.components.hstack",    "HStack");
    LOAD(VStackType_,      "ttyz.components.vstack",    "VStack");
    LOAD(ZStackType_,      "ttyz.components.zstack",    "ZStack");
    LOAD(BoxType_,         "ttyz.components.box",        "Box");
    LOAD(SpacerType_,      "ttyz.components.spacer",    "Spacer");
    LOAD(CondType_,        "ttyz.components.cond",      "Cond");
    LOAD(ForeachType_,     "ttyz.components.foreach",   "Foreach");
    LOAD(ScrollType_,      "ttyz.components.scroll",    "Scroll");
    LOAD(ScrollbarType_,   "ttyz.components.scrollbar",  "Scrollbar");
    LOAD(TableType_,       "ttyz.components.table",     "Table");
    LOAD(TableRowType_,    "ttyz.components.table",     "TableRow");
    LOAD(ScrollStateType_, "ttyz.components.scroll",    "ScrollState");
    LOAD(InputType_,       "ttyz.components.input",     "Input");
#undef LOAD

#define INTERN(var, name) do {                        \
    var = PyUnicode_InternFromString(name);            \
    if (!var) return -1;                               \
} while (0)

    INTERN(a_value,           "value");
    INTERN(a_render_fn,       "render_fn");
    INTERN(s_visible,         "visible");
    INTERN(s_start,           "start");
    INTERN(s_end,             "end");
    INTERN(s_center,          "center");
    INTERN(s_between,         "between");
    INTERN(s_rounded,         "rounded");
    INTERN(s_normal,          "normal");
    INTERN(s_double,          "double");
    INTERN(s_heavy,           "heavy");
#undef INTERN

    PyObject *imod = PyImport_ImportModule("ttyz.components.input");
    if (!imod) return -1;
    py_display_text = PyObject_GetAttrString(imod, "display_text");
    py_display_cursor = PyObject_GetAttrString(imod, "display_cursor");
    Py_DECREF(imod);
    if (!py_display_text || !py_display_cursor) return -1;

#define OFF(var, tp, name) do {                   \
    var = discover_slot_offset(tp, name);         \
    if (var < 0) return -1;                       \
} while (0)

    /* Node base — shared by all subclasses. */
    OFF(off_children,   NodeType_,     "children");
    OFF(off_grow,       NodeType_,     "grow");
    OFF(off_width,      NodeType_,     "width");
    OFF(off_height,     NodeType_,     "height");
    OFF(off_bg,         NodeType_,     "bg");
    OFF(off_overflow,   NodeType_,     "overflow");
    /* Text */
    OFF(off_text_value,     TextType_,    "value");
    OFF(off_text_lines,     TextType_,    "_lines");
    OFF(off_text_visible_w, TextType_,    "_visible_w");
    OFF(off_text_pl,        TextType_,    "pl");
    OFF(off_text_pr,        TextType_,    "pr");
    OFF(off_text_truncation,TextType_,    "truncation");
    OFF(off_text_wrap,      TextType_,    "wrap");
    /* HStack */
    OFF(off_hstack_spacing, HStackType_,  "spacing");
    OFF(off_hstack_jc,      HStackType_,  "justify_content");
    OFF(off_hstack_ai,      HStackType_,  "align_items");
    OFF(off_hstack_wrap,    HStackType_,  "wrap");
    /* VStack */
    OFF(off_vstack_spacing,  VStackType_,  "spacing");
    OFF(off_vstack_needs_measure_pass, VStackType_, "needs_measure_pass");
    /* ZStack */
    OFF(off_zstack_jc,      ZStackType_,  "justify_content");
    OFF(off_zstack_ai,      ZStackType_,  "align_items");
    /* Box */
    OFF(off_box_style,      BoxType_,     "style");
    OFF(off_box_title,      BoxType_,     "title");
    OFF(off_box_padding,    BoxType_,     "padding");
    /* Scroll */
    OFF(off_scroll_state,     ScrollType_,  "state");
    /* Table */
    OFF(off_table_rows,       TableType_,   "rows");
    OFF(off_table_spacing,    TableType_,   "spacing");
    /* TableRow */
    OFF(off_trow_cells,       TableRowType_, "cells");
    /* ScrollState */
    OFF(off_ss_offset,        ScrollStateType_, "offset");
    OFF(off_ss_height,        ScrollStateType_, "height");
    OFF(off_ss_total,         ScrollStateType_, "total");
    OFF(off_ss_follow,        ScrollStateType_, "follow");
    /* Spacer */
    OFF(off_spacer_min_length, SpacerType_, "min_length");
    /* Input */
    OFF(off_input_buffer,      InputType_,     "buffer");
    OFF(off_input_active,      InputType_,     "active");
    OFF(off_input_placeholder, InputType_,     "placeholder");
    /* Scrollbar */
    OFF(off_scrollbar_state,     ScrollbarType_, "state");
    OFF(off_scrollbar_render_fn, ScrollbarType_, "render_fn");
#undef OFF

    render_types_ready = 1;
    return 0;
}

/* ── Slot readers (used throughout render.c) ──────────────────────── */

/* Read a slot as a borrowed PyObject* (no DECREF needed). */
#define SLOT(obj, offset)  (*(PyObject **)((char *)(obj) + (offset)))

/* Read a slot that holds a Python int, returning a C int. */
static inline int slot_int(PyObject *obj, Py_ssize_t offset) {
    return (int)PyLong_AsLong(SLOT(obj, offset));
}

/* Read a slot that holds a Python bool, returning a C int. */
static inline int slot_bool(PyObject *obj, Py_ssize_t offset) {
    return SLOT(obj, offset) == Py_True;
}
