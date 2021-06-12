import os

from conans import ConanFile, tools


class OpenGLRegistryConan(ConanFile):
    name = "opengl-registry"
    license = "Apache-2.0"
    homepage = "https://github.com/KhronosGroup/OpenGL-Registry/"
    url = "https://github.com/KhronosGroup/OpenGL-Registry/"
    description = "OpenGL, OpenGL ES, and OpenGL ES-SC API and Extension Registry"
    topics = ("opengl", "xml", "graphics")
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source"

    def package_id(self):
        self.info.header_only()

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("opengl-registry-{}".format(self.version), self._source_subfolder)

    def package(self):
        self.copy("khrplatform.h", src=os.path.join(self._source_subfolder, "include", "KHR"), dst="include/KHR")
        self.copy("gl.xml", src=os.path.join(self._source_subfolder, "xml"), dst="xml")
        self.copy("glx.xml", src=os.path.join(self._source_subfolder, "xml"), dst="xml")
        self.copy("wgl.xml", src=os.path.join(self._source_subfolder, "xml"), dst="xml")
