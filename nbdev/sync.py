# AUTOGENERATED! DO NOT EDIT! File to edit: nbs/01_sync.ipynb (unless otherwise specified).

__all__ = ['get_name', 'qual_name', 'source_nb', 'relimport2name', 'script2notebook', 'diff_nb_script']

# Cell
from .imports import *
from .export import *

# Cell
def _get_property_name(p):
    "Get the name of property `p`"
    if hasattr(p, 'fget'):
        return p.fget.func.__qualname__ if hasattr(p.fget, 'func') else p.fget.__qualname__
    else: return next(iter(re.findall(r'\'(.*)\'', str(p)))).split('.')[-1]

def get_name(obj):
    "Get the name of `obj`"
    if hasattr(obj, '__name__'):       return obj.__name__
    elif getattr(obj, '_name', False): return obj._name
    elif hasattr(obj,'__origin__'):    return str(obj.__origin__).split('.')[-1] #for types
    elif type(obj)==property:          return _get_property_name(obj)
    else:                              return str(obj).split('.')[-1]

# Cell
def qual_name(obj):
    "Get the qualified name of `obj`"
    if hasattr(obj,'__qualname__'): return obj.__qualname__
    if inspect.ismethod(obj):       return f"{get_name(obj.__self__)}.{get_name(fn)}"
    return get_name(obj)

# Cell
def source_nb(func, is_name=None, return_all=False, mod=None):
    "Return the name of the notebook where `func` was defined"
    is_name = is_name or isinstance(func, str)
    if mod is None: mod = get_nbdev_module()
    index = mod.index
    name = func if is_name else qual_name(func)
    while len(name) > 0:
        if name in index: return (name,index[name]) if return_all else index[name]
        name = '.'.join(name.split('.')[:-1])

# Cell
_re_cell = re.compile(r'^# Cell|^# Internal Cell|^# Comes from\s+(\S+), cell')

# Cell
def _split(code):
    lines = code.split('\n')
    nbs_path = Config().nbs_path.relative_to(Config().config_file.parent)
    prefix = '' if nbs_path == Path('.') else f'{nbs_path}/'
    default_nb = re.search(f'File to edit: {prefix}(\\S+)\\s+', lines[0]).groups()[0]
    s,res = 1,[]
    while _re_cell.search(lines[s]) is None: s += 1
    e = s+1
    while e < len(lines):
        while e < len(lines) and _re_cell.search(lines[e]) is None: e += 1
        grps = _re_cell.search(lines[s]).groups()
        nb = grps[0] or default_nb
        content = lines[s+1:e]
        while len(content) > 1 and content[-1] == '': content = content[:-1]
        res.append((nb, '\n'.join(content)))
        s,e = e,e+1
    return res

# Cell
def relimport2name(name, mod_name):
    "Unwarps a relative import in `name` according to `mod_name`"
    if mod_name.endswith('.py'): mod_name = mod_name[:-3]
    mods = mod_name.split(os.path.sep)
    i = last_index(Config().lib_name, mods)
    mods = mods[i:]
    if name=='.': return '.'.join(mods[:-1])
    i = 0
    while name[i] == '.': i += 1
    return '.'.join(mods[:-i] + [name[i:]])

# Cell
#Catches any from .bla import something and catches .bla in group 1, the imported thing(s) in group 2.
_re_loc_import = re.compile(r'(^\s*)from (\.\S*) import (.*)$')
_re_loc_import1 = re.compile(r'(^\s*)import (\.\S*)(.*)$')

# Cell
def _deal_loc_import(code, fname):
    def _replace(m):
        sp,mod,obj = m.groups()
        return f"{sp}from {relimport2name(mod, fname)} import {obj}"
    def _replace1(m):
        sp,mod,end = m.groups()
        return f"{sp}import {relimport2name(mod, fname)}{end}"
    return '\n'.join([_re_loc_import1.sub(_replace1, _re_loc_import.sub(_replace,line)) for line in code.split('\n')])

# Cell
def _script2notebook(fname, dic, silent=False):
    "Put the content of `fname` back in the notebooks it came from."
    if os.environ.get('IN_TEST',0): return  # don't export if running tests
    fname = Path(fname)
    with open(fname, encoding='utf8') as f: code = f.read()
    splits = _split(code)
    rel_name = fname.absolute().resolve().relative_to(Config().lib_path)
    key = str(rel_name.with_suffix(''))
    assert len(splits)==len(dic[key]), f'"{rel_name}" exported from notebooks should have {len(dic[key])} cells but has {len(splits)}.'
    assert all([c1[0]==c2[1]] for c1,c2 in zip(splits, dic[key]))
    splits = [(c2[0],c1[0],c1[1]) for c1,c2 in zip(splits, dic[key])]
    nb_fnames = {Config().nbs_path/s[1] for s in splits}
    for nb_fname in nb_fnames:
        nb = read_nb(nb_fname)
        for i,f,c in splits:
            c = _deal_loc_import(c, str(fname))
            if f == nb_fname.name:
                flags = split_flags_and_code(nb['cells'][i], str)[0]
                nb['cells'][i]['source'] = flags + '\n' + c.replace('#nbdev_comment ', '')
        NotebookNotary().sign(nb)
        nbformat.write(nb, str(nb_fname), version=4)

    if not silent: print(f"Converted {rel_name}.")

# Cell
def script2notebook(fname=None, silent=False):
    "Update the notebooks from any changes made in the modules corresponding to `fname`"
    if os.environ.get('IN_TEST',0): return
    dic = notebook2script(silent=True, to_dict=True)
    exported = get_nbdev_module().modules

    if fname is None:
        files = [f for f in Config().lib_path.glob('**/*.py') if str(f.relative_to(Config().lib_path)) in exported]
    else: files = glob.glob(fname)
    [ _script2notebook(f, dic, silent=silent) for f in files]

# Cell
import subprocess
from distutils.dir_util import copy_tree

# Cell
def diff_nb_script():
    "Print the diff between the notebooks and the library in lib_path"
    lib_folder = Config().lib_path
    with tempfile.TemporaryDirectory() as d1, tempfile.TemporaryDirectory() as d2:
        copy_tree(Config().lib_path, d1)
        notebook2script(silent=True)
        copy_tree(Config().lib_path, d2)
        shutil.rmtree(Config().lib_path)
        shutil.copytree(d1, str(Config().lib_path))
        for d in [d1, d2]:
            if (Path(d)/'__pycache__').exists(): shutil.rmtree(Path(d)/'__pycache__')
        res = subprocess.run(['diff', '-ru', d1, d2], stdout=subprocess.PIPE)
        print(res.stdout.decode('utf-8'))