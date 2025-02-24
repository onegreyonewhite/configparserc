# Fast ConfigParser

[![Pipeline status](https://gitlab.com/onegreyonewhite/configparserc/badges/master/pipeline.svg)](https://gitlab.com/onegreyonewhite/configparserc/commits/master)
[![Coverage report](https://gitlab.com/onegreyonewhite/configparserc/badges/master/coverage.svg)](https://gitlab.com/onegreyonewhite/configparserc/pipelines)
[![](https://badge.fury.io/py/configparserc.svg)](https://badge.fury.io/py/configparserc)

Python (Cython) based implementation of ConfigParser based on POSIX and stdlib functions.  
Wrapped via Cython, uses POSIX stat and libc stdio functions for reading files.

Support converting values in formats:

- `StrType` - force convert to string all values (defaults too).
- `IntType` - convert values to integer (include suffixes 'K', 'M' and 'G' multiples of 1000).
- `BytesSizeType` - convert values to integer size of bytes (include suffixes 'K', 'M' and 'G' multiples of 1024).
- `BoolType` - convert `'False'`, `'false'`, `'True'` and `'true'` to valid Python bool type.
- `IntSecondsType` - convert time to seconds. Uses the `pytimeparse` python package.
- `TimedeltaType` - convert time to timedelta/relativedelta (if installed). Uses the `pytimeparse` python package.
- `ListType` - convert a string with values separated by a symbol (default is comma) to a list of values.
- `JsonType` - convert a JSON value to a Python value.

## Usage

Install the package in your environment:

```bash
pip install configparserc
```

Example code for parse ini-config:

```python
import os
import configparserc


class MainSection(configparserc.AppendSection):
    """
    Simple section where:
    * some_int_key has int value;
    * some_bool_key has bool value;
    * some_list_key has semicolon separated list value;
    * some_other_key has int value in bytes.

    All values append or override defaults.
    """
    type_some_int_key = configparserc.IntType()
    type_some_bool_key = configparserc.BoolType()
    type_some_list_key = configparserc.ListType(separator=';')
    type_some_other_key = configparserc.ListType(separator=';')


config = configparserc.ConfigParserC(
    # Override section class for section `main`
    section_overload={'main': MainSection},
    # Set defaults for all sections.
    section_defaults={
        'main': {
            'some_int_key': "123",
            'some_bool_key': "false",
            'some_list_key': "a;c;d"
        }
    },
    # Allow usage of values from the environment
    # via "{ENVIRONMENT_VAR}" placeholders.
    format_kwargs=os.environ.copy()
)

config.parse_files(['/path/to/ini/config', '/other/path/to/ini/config'])
config.parse_text('''
[main]
# Support comments
; in different ini formats.
int_key = 1234
''')

config_as_dict = config.all()
```

## Authors

**Author:**  
Sergey Klyuykov <onegreyonewhite@mail.ru>

**Contributor(s):**  
Kirill Bychkov <kirill970528@yandex.ru>

## License

The ConfigParserC Project ([https://gitlab.com/onegreyonewhite/configparserc](https://gitlab.com/onegreyonewhite/configparserc))  
Copyright (C) 2019-2025 Sergey Klyuykov

Licensed under the Apache License, Version 2.0 (the "License");  
you may not use this file except in compliance with the License.  
You may obtain a copy of the License at:

[http://www.apache.org/licenses/LICENSE-2.0](http://www.apache.org/licenses/LICENSE-2.0)

Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS,  
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.  
See the License for the specific language governing permissions and limitations under the License.
