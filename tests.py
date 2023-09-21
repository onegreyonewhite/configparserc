import os
import unittest
from copy import deepcopy
from datetime import timedelta

try:
    from configparserc import *
except ImportError:  # nocv
    import pyximport
    pyximport.install(
        language_level=3,
        setup_args=dict(
            include_dirs=[
                '/'.join([os.path.dirname(__file__), 'include']),
                '/'.join(['.', os.path.dirname(__file__), 'include']),
            ]
        )
    )
    from configparserc import *


class ConfigTestCase(unittest.TestCase):
    def setUp(self):
        super().setUp()
        self._maxDiff = self.maxDiff
        self.maxDiff = 4096

    def tearDown(self) -> None:
        super().tearDown()
        self.maxDiff = self._maxDiff

    def test_file_reader(self):
        class TestFirstSection(Section):
            types_map = {
                'key3': BoolType(), 'sec': IntSecondsType(), 'lst': ListType(), 'emptylst': ListType(),
                'lstdot': ListType(separator='.'), 'tostr': StrType()
            }
            type_key2 = IntType()
            type_key_from_yaml = IntType()
            type_jsonkey = JsonType()
            type_keyint1 = IntType()
            type_keyint2 = IntType()
            type_keyint3 = IntType()
            type_keybytes1 = BytesSizeType()
            type_keybytes2 = BytesSizeType()
            type_keybytes3 = BytesSizeType()
            type_keybytes4 = BytesSizeType()
            type_timedelta = TimedeltaType()

        class TestSecondSection(Section):
            pass

        class TestThirdSection(Section):
            pass

        class TestSectionFunctional(Section):
            pass

        class TestKeyHandler(Section):
            def key_handler_to_all(self, key):
                return super().key_handler_to_all(key).upper()

        class TestDefaultSettings(Section):
            type_default2 = IntType()

        class DBDefaultSettings(Section):
            type_port = IntType()

        class TestAppendSection(AppendSection):
            pass

        class TestBasedOnParentSection(TestKeyHandler):
            def key_handler_to_all(self, key):
                result = super().key_handler_to_all(key)
                if self.parent.get(key, None) == '1':
                    return result
                return result.lower()

        class TestConfigParserC(ConfigParserC):
            section_class_another = TestSecondSection
            section_class_append = TestAppendSection
            section_overload = {
                'another.sub': TestThirdSection,
                'another.keyhandler': TestKeyHandler,
                'add_item.subs': TestFirstSection,
                'db': DBDefaultSettings,
                'parent': TestAppendSection,
                'parent.options': TestBasedOnParentSection,
            }
            defaults = {
                'parent': {},
                'append': {
                    'exists': '123'
                },
                'withdefault': {
                    'default1': 'default_value1',
                    'default2': 159,
                    'default3': 'True',
                    'default4': '1209600',
                    'default5': '("one", "two", "three")',
                    'defaultsub': {
                        'default_subs_key': 'default_subs_value'
                    }
                },
                'another': {
                    't1': 't2'
                },
                'db': {
                    'engine': 'django.db.backends.sqlite3',
                    'name': 'db.test.sqlite3',
                    'test': {
                        'serialize': 'false'
                    }
                },
                'subdef': {
                    'default': {
                        'def1': 'test',
                        'def2': 'test2',
                    }
                }
            }

        format_kwargs = dict(
            INTEGER=22, STRING='kwargs_str'
        )
        test_parser = TestConfigParserC(
            section_overload=dict(main=TestFirstSection, add_item=TestSectionFunctional,
                                  withdefault=TestDefaultSettings),
            format_kwargs=format_kwargs,
            format_exclude_sections=('unformat',)
        )
        files_list = ['test_conf.ini', 'test_conf2.ini', 'test_conf3.ini', 'test_yaml_config.yaml']
        files_list.append('sljkdhkjlsjdglksdjsdhfskjfwehwioejksn')
        files_list = map(lambda x: os.path.join(os.path.dirname(__file__), x), files_list)
        config_text = '[another]\nanother_key1 = some_new_value'
        config_test_default = '[db]\nengine = django.db.backends.mysql\nname = vsttest\nuser = vsttest\npassword = vsttest\nhost = localhost\nport = 3306\n[db.options]\ninit_command = some_command'
        config_test_default += '\n[unformat]\nkey = ${test}\n'

        self.assertEqual(list(test_parser.keys()), ['parent', 'append', 'withdefault', 'another', 'db', 'subdef'])

        config_data = {
            'parent': {
                'test': '1',
                'options': {
                    'test': 'value',
                    "test2": 'value',
                }
            },
            'main': {
                'key1': 'value4',
                'key2': 251,
                'key3': True,
                'key_from_yaml': 123,
                'keybytes1': 2560,
                'keybytes2': 3221225472,
                'keybytes3': 2,
                'keybytes4': 18,
                'keyint1': 2000,
                'keyint2': 2000000,
                'keyint3': 2000000000,
                'sec': 1209600,
                'lst': ('test', '2', '5', 'str'),
                'lstdot': ('test', '2', '5', 'str'),
                'emptylst': (),
                'key22': '/tmp/kwargs_str',
                'jsonkey': [{"jkey": "jvalue"}],
                'formatstr': 'value4',
                'formatint': '251',
                'without_type': '123',
                'timedelta': timedelta(days=4, hours=5, minutes=6, seconds=7, microseconds=8000),
            },
            'to_json': {
                "jkey": "jvalue"
            },
            'another': {
                'another_key1': 'some_new_value',
                'another_key2': 'another_value2',
                'another_key3': 'another_value3',
                'keyhandler': {
                    'handler': 'work'
                },
                'sub': {
                    'another_key1': 'another_value2',
                    'another_key2': 'another_value2'
                },
                'empty': {},
            },
            'withdefault': {
                'default1': 'default_value1',
                'default2': 159,
                'default3': 'True',
                'default4': '1209600',
                'default5': '("one", "two", "three")',
                'defaultsub': {
                    'default_subs_key': 'default_subs_value'
                }
            },
            'deep': {"deep": {"deep": {"options": {"key": "value"}}}},
            'gettype': {
                'toint': '257',
                'tobool': 'False',
                'tolist': 'first,second,third',
                'tointsec': '2w',
                'tojson': '{"jsonkey": "jsonvalue"}'
            },
            'db': {
                'engine': 'django.db.backends.mysql',
                'name': 'vsttest',
                'user': 'vsttest',
                'password': 'vsttest',
                'host': 'localhost',
                'port': 3306,
                'options': {
                    'init_command': 'some_command'
                }
            },
            'onlysubs': {
                'sub1': {},
                'sub2': {},
                'sub3': {},
            },
            'withoutsubs': {
                'withoutsubs1': 'val1',
                'withoutsubs2': 'val2',
                'withoutsubs3': 'val3',
            },
            'subdef': {
                'default': {
                    'def1': 'test',
                    'def2': 'test2',
                }
            },
            'test': {
                'rec': {
                    'recurs_key': 'recurseval'
                }
            },
            'append': {
                'exists': '123',
                'new': '1234'
            },
            'yaml_section': {
                "item": "new string data",
                "item2": '123'
            },
            'unformat': {
                "key": "${test}"
            },
        }
        final_data = deepcopy(config_data)
        final_data['parent']['options']['TEST'] = final_data['parent']['options'].pop('test')
        final_data['another']['keyhandler']['HANDLER'] = final_data['another']['keyhandler'].pop('handler')

        # Parse files and text
        test_parser.parse_files(files_list)
        test_parser.parse_text(config_text)
        test_parser.parse_text(config_test_default)
        test_parser.parse_text('')
        # Check is filled config
        self.assertTrue(test_parser)

        # Compare sections classes, with setuped
        self.assertTrue(isinstance(test_parser['main'], TestFirstSection), type(test_parser['main']))
        self.assertTrue(isinstance(test_parser['another']['keyhandler'], TestKeyHandler))
        self.assertTrue(isinstance(test_parser['another'], TestSecondSection))
        self.assertTrue(isinstance(test_parser['another']['sub'], TestThirdSection))

        # Compare data
        self.assertEqual(config_data['main'], test_parser['main'], repr(test_parser['main']))
        self.assertEqual(config_data['withdefault'], test_parser['withdefault'], repr(test_parser['withdefault']))
        self.assertDictEqual(test_parser, config_data, repr(test_parser))
        self.assertEqual(len(str(test_parser)), len(str(config_data)))
        self.assertDictEqual(test_parser.all(), final_data)

        # Test method `all()` for config and compare with data
        self.assertDictEqual(test_parser['main'].all(), config_data['main'])

        # Check types for vars, that was setup
        self.assertTrue(isinstance(test_parser['main']['key2'], int))
        self.assertTrue(isinstance(test_parser['main']['key3'], bool))
        self.assertTrue(isinstance(test_parser['main']['sec'], int))
        self.assertTrue(isinstance(test_parser['main']['lst'], tuple))
        self.assertTrue(isinstance(test_parser['main']['emptylst'], tuple))

        # Check __setitem__ and __getitem__ for config
        test_parser['add_item'] = dict()
        test_parser['add_item']['subs'] = dict()
        self.assertTrue(isinstance(test_parser['add_item'], TestSectionFunctional))
        self.assertTrue(isinstance(test_parser['add_item']['subs'], TestFirstSection))
        self.assertDictEqual(test_parser['add_item'], {'subs': {}})

        # Check non-existed section
        self.assertDictEqual(test_parser.get('no_section', {}), {})
        self.assertDictEqual(test_parser['no_section'], {})
        self.assertTrue(not test_parser['add_item'] == {'subs': {"extra": 1}})
        self.assertTrue(not test_parser['no_section'] == 1)

        # Make manual typeconversation, and two times conversation same value
        self.assertEqual(test_parser['main'].getbytes('keybytes1'), 2560)
        self.assertEqual(test_parser['main']['without_type'], '123')
        self.assertEqual(test_parser['main'].get('get_nonexists_val', 1), 1)
        self.assertEqual(test_parser['main'].getint('key2'), 251)
        self.assertEqual(test_parser['gettype'].getint('toint'), 257)
        self.assertTrue(isinstance(test_parser['gettype'].getint('toint'), int))

        self.assertEqual(test_parser['main'].getboolean('key3'), True)
        self.assertEqual(test_parser['gettype'].getboolean('tobool'), False)
        self.assertTrue(isinstance(test_parser['gettype'].getboolean('tobool'), bool))

        self.assertEqual(test_parser['main'].getseconds('sec'), 1209600)
        self.assertEqual(test_parser['gettype'].getseconds('tointsec'), 1209600)
        self.assertTrue(isinstance(test_parser['gettype'].getseconds('tointsec'), int))

        self.assertEqual(test_parser['gettype'].getlist('tolist'), ('first', 'second', 'third'))
        self.assertTrue(isinstance(test_parser['gettype'].getlist('tolist'), tuple))
        self.assertEqual(test_parser['main'].getlist('lstdot', '.'), ('test', '2', '5', 'str'))
        self.assertEqual(test_parser['main'].getlist('key1', '.'), ('value4',))
        self.assertEqual(test_parser['main'].getlist('key2', '.'), (251,))

        self.assertDictEqual(test_parser['gettype'].getjson('tojson'), {'jsonkey': 'jsonvalue'})
        self.assertEqual(test_parser['main'].getjson('key2'), 251)
        self.assertDictEqual(test_parser['another'].getjson('keyhandler'), {'handler': 'work'})

        test_parser['add_item']['subs']['tostr'] = 25
        self.assertEqual(test_parser['add_item']['subs']['tostr'], '25')

        # Test `get()` method of config
        self.assertEqual(test_parser.get('main').get('key1'), 'value4')

        # Check file exist handler
        test_parser.parse_file('123.txt')

        # Check parser exception handler
        with self.assertRaises(ConfigParserException):
            test_parser.parse_text('qwerty')

        with self.assertRaises(ConfigParserException):
            test_parser.parse_file(os.path.join(os.path.dirname(__file__), 'test_conf_err.ini'))

        with self.assertRaises(ParseError):
            test_parser.parse_file(os.path.join(os.path.dirname(__file__), 'test_conf_err2.ini'))

        with self.assertRaises(ConfigParserException):
            test_parser.parse_text('[another]\nanother_key1')

        with self.assertRaises(ConfigParserException):
            test_parser.parse_text('[another]\n=another_key1')

        with self.assertRaises(ConfigParserException):
            test_parser.parse_text('[another]\n =another_key1')

        with self.assertRaises(ConfigParserException):
            test_parser.parse_text('[another]\n  =another_key1')

        conf_empty_default = ConfigParserC()
        test_sect = Section('test_sect_name', conf_empty_default, type_map={'test_key': 'test_val'})
        test_parser.parse_text('\0')
        with self.assertRaises(KeyError):
            test_sect['kk']
        with self.assertRaises(KeyError):
            test_sect.get('kk')

        parser_from_out_str = TestConfigParserC(
            section_overload=dict(main=TestFirstSection, add_item=TestSectionFunctional,
                                  withdefault=TestDefaultSettings),
            format_kwargs=format_kwargs
        )
        parser_from_out_str.parse_text(test_parser.generate_config_string())
        self.assertDictEqual(parser_from_out_str.all(), test_parser.all())

        # Check section properties
        self.assertTrue(test_parser['main'].main_config is test_parser)
        self.assertEqual(test_parser['main'].parent, None)
        self.assertTrue(test_parser['deep']['deep']['deep']['options'].parent is test_parser['deep']['deep']['deep'])

    def test_sections_custom_working(self):
        class TestFirstLevelSection(Section):
            type_key1 = IntType()

        class TestSecondLevelSection(Section):
            type_key1 = IntType()


        config = ConfigParserC(section_overload={
            'first': TestFirstLevelSection,
            'first.second': TestSecondLevelSection,
        })

        config.parse_text('')

        section = config.get_section_instance('first')
        section.update(**{"second": {'key1': "3"}})

        section_data = section.all()
        self.assertEqual(section_data['second']['key1'], 3)

        config.clear()
        self.assertFalse(config)

        config['first'] = {"second": {'key1': "3"}}
        section_data = section.all()
        self.assertEqual(section_data['second']['key1'], 3)


if __name__ == '__main__':
    unittest.main('tests')
