import os

from conans import ConanFile, CMake, tools


class RTMidiConan(ConanFile):
    name = "rtmidi"
    license = "RtMidi"
    homepage = "https://github.com/thestk/rtmidi"
    url = "https://github.com/thestk/rtmidi"
    settings = "os", "compiler", "build_type", "arch"
    description = "A set of C++ classes that provide a common API for realtime MIDI input/output across Linux (ALSA & JACK), Macintosh OS X (CoreMIDI) and Windows (Multimedia)"
    topics = ("midi", "audio")
    generators = ['cmake', 'cmake_find_package']

    @property
    def _source_subfolder(self):
        return "source"

    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions['BUILD_SHARED_LIBS'] = True
        cmake.definitions['BUILD_TESTING'] = False
        return cmake

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("rtmidi-{}".format(self.version), self._source_subfolder)

    def build(self):
        cmake = self._configure_cmake()
        cmake.configure(source_folder=os.path.join(self.source_folder, self._source_subfolder), build_folder=self.build_folder)
        cmake.build()

    def package(self):
        self.copy('LICENSE', dst='licenses', src=self._source_subfolder)

        cmake = self._configure_cmake()
        cmake.install()

        tools.rmdir(os.path.join(self.package_folder, 'share'))
        tools.rmdir(os.path.join(self.package_folder, 'lib', 'pkgconfig'))

    def package_info(self):
        self.cpp_info.libs = ["rtmidi"]
