# cython: c_string_type=str, c_string_encoding=utf8
'''
The ConfigParserC Project (https://gitlab.com/onegreyonewhite/configparserc)
Copyright (C) 2019-2020 Sergey Klyuykov

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

'''

from libc.stdio cimport FILE, fopen, fread, fwrite, fflush, fclose, feof, getline
from libc.string cimport strlen
from posix.stat cimport stat, struct_stat
from libc.stdlib cimport malloc, free


def get_file_value(filename, default='', raise_error=False, strip=True):
    result = default

    try:
        result = File(filename).read()
        if strip:
            result = result.strip()
    except IOError:
        if raise_error:
            raise

    return result


cdef class File:
    cdef:
        FILE* file
        char* buff
        long int _size
        const char* filename
        const char* mode
        struct_stat st

    def __cinit__(self, const char* filename, const char* mode = 'r'):
        self.filename = filename
        self.mode = mode
        stat(self.filename, &self.st)
        self.file = self._open()

    cdef allowed(self):
        if not self.file == NULL:
            return True

    cdef FILE*_open(self):
        return fopen(self.filename, self.mode)

    cdef long int size(self):
        if not self.allowed():
            raise IOError('File is not found.')
        with nogil:
            return self.st.st_size

    cdef _read(self):
        cdef long int size, typesize

        with nogil:
            size = self.st.st_size
            typesize = sizeof(char)
            if self.buff == NULL:
                self.buff = <char*> malloc(size * typesize)
                if self.buff == NULL: raise MemoryError('low memory')
                read = fread(self.buff, typesize, size, self.file)

        return self.buff[:size]

    def read(self):
        if not self.allowed():
            raise IOError('File is not found.')
        return self._read()

    cdef void _write(self, const char* value):
        size = len(value)
        typesize = sizeof(char)
        with nogil:
            fwrite(value, typesize, size, self.file)

    def write(self, value):
        if self.mode == 'r':
            raise IOError('File should opened for writing')
        if not self.allowed():
            raise IOError('File is not found.')
        self._write(value)

    cdef int _flush(self):
        return fflush(self.file)

    def flush(self):
        return self._flush()

    cdef int _feof(self):
        return feof(self.file)

    def feof(self):
        return self._feof()

    cdef char* _readline(self, int replace_newline = 0):
        cdef:
            char* line
            size_t count
        count = 0
        line = NULL
        if getline(&line, &count, self.file) != -1:
            if replace_newline == 1:
                line[strlen(line) - 1] = b'\0'
            return line
        return ''

    def readline(self):
        return self._readline()

    def readlines(self, replace_newline = 1):
        while self._feof() != 1:
            yield self._readline(replace_newline=replace_newline)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        del self

    def __len__(self):
        return self.size()

    def __dealloc__(self):
        with nogil:
            if self.buff is not NULL:
                free(self.buff)
        self.close()

    cdef void close(self):
        with nogil:
            if self.file is not NULL:
                fclose(self.file)
