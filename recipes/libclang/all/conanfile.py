from conans.errors import ConanInvalidConfiguration
from conans import ConanFile, CMake, tools

from collections import defaultdict
import json
import re
import os.path
import os


class LibClangConan(ConanFile):
    name = 'libclang'
    description = (
        'A toolkit for the construction of highly optimized compilers,'
        'optimizers, and runtime environments. This package is based '
        'on the official llvm-core package, but also includes libclang.'
    )
    license = 'Apache-2.0 WITH LLVM-exception'
    topics = ('conan', 'llvm', 'clang')
    homepage = 'https://github.com/llvm/llvm-project/tree/master/llvm'
    url = 'https://github.com/conan-io/conan-center-index'

    settings = ('os', 'arch', 'compiler')
    options = {
        'shared': [True, False],
        'fPIC': [True, False],
        'components': 'ANY',
        'targets': 'ANY',
        'exceptions': [True, False],
        'rtti': [True, False],
        'threads': [True, False],
        'lto': ['On', 'Off', 'Full', 'Thin'],
        'static_stdlib': [True, False],
        'unwind_tables': [True, False],
        'expensive_checks': [True, False],
        'use_perf': [True, False],
        'use_sanitizer': [
            'Address',
            'Memory',
            'MemoryWithOrigins',
            'Undefined',
            'Thread',
            'DataFlow',
            'Address;Undefined',
            'None'
        ],
        'with_clang': [True, False],
        'with_ffi': [True, False],
        'with_zlib': [True, False],
        'with_xml2': [True, False]
    }
    default_options = {
        'shared': False,
        'fPIC': True,
        'components': 'all',
        'targets': 'all',
        'exceptions': True,
        'rtti': True,
        'threads': True,
        'lto': 'Off',
        'static_stdlib': False,
        'unwind_tables': True,
        'expensive_checks': False,
        'use_perf': False,
        'use_sanitizer': 'None',
        'with_clang': True,
        'with_ffi': False,
        'with_zlib': True,
        'with_xml2': True
    }

    exports_sources = ['CMakeLists.txt', 'patches/*']
    generators = ['cmake', 'cmake_find_package']
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return 'source'

    def _supports_compiler(self):
        compiler = self.settings.compiler.value
        version = tools.Version(self.settings.compiler.version)
        major_rev, minor_rev = int(version.major), int(version.minor)

        unsupported_combinations = [
            [compiler == 'gcc', major_rev == 5, minor_rev < 1],
            [compiler == 'gcc', major_rev < 5],
            [compiler == 'clang', major_rev < 4],
            [compiler == 'apple-clang', major_rev < 9],
            [compiler == 'Visual Studio', major_rev < 15]
        ]
        if any(all(combination) for combination in unsupported_combinations):
            message = 'unsupported compiler: "{}", version "{}"'
            raise ConanInvalidConfiguration(message.format(compiler, version))

    def _patch_sources(self):
        for patch in self.conan_data.get('patches', {}).get(self.version, []):
            tools.patch(**patch)

    def _patch_build(self):
        if os.path.exists('FindIconv.cmake'):
            tools.replace_in_file('FindIconv.cmake', 'iconv charset', 'iconv')

    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions['BUILD_SHARED_LIBS'] = False
        cmake.definitions['CMAKE_SKIP_RPATH'] = True
        cmake.definitions['CMAKE_POSITION_INDEPENDENT_CODE'] = \
            self.options.get_safe('fPIC', default=False) or self.options.shared

        if not self.options.shared:
            cmake.definitions['DISABLE_LLVM_LINK_LLVM_DYLIB'] = True
        # cmake.definitions['LLVM_LINK_DYLIB'] = self.options.shared

        cmake.definitions['LLVM_TARGET_ARCH'] = 'host'
        cmake.definitions['LLVM_TARGETS_TO_BUILD'] = self.options.targets
        cmake.definitions['LLVM_BUILD_LLVM_DYLIB'] = self.options.shared
        cmake.definitions['LLVM_DYLIB_COMPONENTS'] = self.options.components
        cmake.definitions['LLVM_ENABLE_PIC'] = \
            self.options.get_safe('fPIC', default=False)

        cmake.definitions['LLVM_ABI_BREAKING_CHECKS'] = 'WITH_ASSERTS'
        cmake.definitions['LLVM_ENABLE_WARNINGS'] = True
        cmake.definitions['LLVM_ENABLE_PEDANTIC'] = True
        cmake.definitions['LLVM_ENABLE_WERROR'] = False

        cmake.definitions['LLVM_TEMPORARILY_ALLOW_OLD_TOOLCHAIN'] = True
        cmake.definitions['LLVM_USE_RELATIVE_PATHS_IN_DEBUG_INFO'] = False
        cmake.definitions['LLVM_BUILD_INSTRUMENTED_COVERAGE'] = False
        cmake.definitions['LLVM_OPTIMIZED_TABLEGEN'] = True
        cmake.definitions['LLVM_REVERSE_ITERATION'] = False
        cmake.definitions['LLVM_ENABLE_BINDINGS'] = False
        cmake.definitions['LLVM_CCACHE_BUILD'] = False

        cmake.definitions['LLVM_INCLUDE_TOOLS'] = True
        cmake.definitions['LLVM_INCLUDE_EXAMPLES'] = False
        cmake.definitions['LLVM_INCLUDE_TESTS'] = False
        cmake.definitions['LLVM_INCLUDE_BENCHMARKS'] = False
        cmake.definitions['LLVM_APPEND_VC_REV'] = False
        cmake.definitions['LLVM_BUILD_DOCS'] = False
        cmake.definitions['LLVM_ENABLE_IDE'] = False

        cmake.definitions['LLVM_ENABLE_EH'] = self.options.exceptions
        cmake.definitions['LLVM_ENABLE_RTTI'] = self.options.rtti
        cmake.definitions['LLVM_ENABLE_THREADS'] = self.options.threads
        cmake.definitions['LLVM_ENABLE_LTO'] = self.options.lto
        cmake.definitions['LLVM_STATIC_LINK_CXX_STDLIB'] = \
            self.options.static_stdlib
        cmake.definitions['LLVM_ENABLE_UNWIND_TABLES'] = \
            self.options.unwind_tables
        cmake.definitions['LLVM_ENABLE_EXPENSIVE_CHECKS'] = \
            self.options.expensive_checks
        cmake.definitions['LLVM_ENABLE_ASSERTIONS'] = \
            self.settings.build_type == 'Debug'

        cmake.definitions['LLVM_USE_NEWPM'] = False
        cmake.definitions['LLVM_USE_OPROFILE'] = False
        cmake.definitions['LLVM_USE_PERF'] = self.options.use_perf
        if self.options.use_sanitizer == 'None':
            cmake.definitions['LLVM_USE_SANITIZER'] = ''
        else:
            cmake.definitions['LLVM_USE_SANITIZER'] = \
                self.options.use_sanitizer

        cmake.definitions['LLVM_ENABLE_Z3_SOLVER'] = False
        cmake.definitions['LLVM_ENABLE_LIBPFM'] = False
        cmake.definitions['LLVM_ENABLE_LIBEDIT'] = False
        cmake.definitions['LLVM_ENABLE_FFI'] = self.options.with_ffi
        cmake.definitions['LLVM_ENABLE_ZLIB'] = \
            self.options.get_safe('with_zlib', False)
        cmake.definitions['LLVM_ENABLE_LIBXML2'] = \
            self.options.get_safe('with_xml2', False)

        #if self.options.with_clang:
        cmake.definitions['LLVM_ENABLE_PROJECTS'] = 'clang'

        return cmake

    def config_options(self):
        if self.settings.os == 'Windows':
            del self.options.fPIC
            del self.options.with_zlib
            del self.options.with_xml2

    def requirements(self):
        if self.options.with_ffi:
            raise ConanInvalidConfiguration('Building with ffi is not supported.')
            #self.requires('libffi/3.3')

        if self.options.get_safe('with_zlib', False):
            self.requires(self.conan_data["dependencies"][self.version]["zlib"])

        if self.options.get_safe('with_xml2', False):
            self.requires(self.conan_data["dependencies"][self.version]["libxml2"])

    def configure(self):
        if self.options.shared:  # Shared builds disabled just due to the CI
            del self.options.fPIC

        # if self.settings.os == 'Windows' and self.options.shared:
        #     message = 'Shared builds not supported on Windows'
        #     raise ConanInvalidConfiguration(message)
        if self.options.exceptions and not self.options.rtti:
            message = 'Cannot enable exceptions without rtti support'
            raise ConanInvalidConfiguration(message)
        self._supports_compiler()

    def source(self):
        tools.get(**self.conan_data['sources'][self.version])
        os.rename('libclang-{}'.format(self.version), self._source_subfolder)
        self._patch_sources()

    def build(self):
        self._patch_build()
        cmake = self._configure_cmake()
        cmake.configure(source_folder=self.source_folder + '/source/llvm', build_folder=self.build_folder)
        cmake.build()

    def package(self):
        self.copy('llvm/LICENSE.TXT', dst='licenses', src=self._source_subfolder)
        self.copy('clang/LICENSE.TXT', dst='licenses', src=self._source_subfolder)

        cmake = self._configure_cmake()
        cmake.install()

        tools.remove_files_by_mask(self.package_folder, "*.pdb")
        tools.remove_files_by_mask(self.package_folder, "*.exe")
        tools.remove_files_by_mask(self.package_folder, "*.py")
        tools.rmdir(os.path.join(self.package_folder, 'share'))
        tools.rmdir(os.path.join(self.package_folder, 'libexec'))

    def package_info(self):
        if self.settings.os == 'Windows':
            self.cpp_info.libs = ["libclang"]
        else:
            self.cpp_info.libs = ["clang"]
