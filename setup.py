import sys
from vstcompile import make_setup, load_requirements

ext_list = [
    'configparserc',
]

if 'develop' in sys.argv:
    ext_list = []

make_setup(
    ext_modules_list=ext_list,
)
