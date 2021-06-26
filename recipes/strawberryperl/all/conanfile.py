import os
from conans import ConanFile, tools
from conans.errors import ConanInvalidConfiguration


class StrawberryperlConan(ConanFile):
    name = "strawberryperl"
    description = "Strawbery Perl for Windows. Useful as build_require"
    license = "GNU Public License or the Artistic License"
    homepage = "http://strawberryperl.com"
    url = "https://github.com/conan-io/conan-center-index"
    topics = ("conan", "installer", "perl", "windows")
    settings = "os", "arch"
    short_paths = True

    def configure(self):
        if self.settings.os != "Windows":
            raise ConanInvalidConfiguration("Only windows supported for Strawberry Perl.")
        if self.settings.arch != "x86_64":
            raise ConanInvalidConfiguration("Only 64-bit is supported for Strawberry Perl.")

    def build(self):
        tools.get(**self.conan_data["sources"][self.version])

    def package(self):
        extracted_dir = "strawberry-perl-" + self.version
        self.copy(pattern="License.rtf*", src=os.path.join(extracted_dir, "licenses"), dst="licenses")
        self.copy(pattern="*", src=os.path.join(extracted_dir, "perl", "bin"), dst="bin")
        self.copy(pattern="*", src=os.path.join(extracted_dir, "perl", "lib"), dst="lib")
        self.copy(pattern="*", src=os.path.join(extracted_dir, "perl", "vendor", "lib"), dst="vendor/lib")
        self.copy(pattern="*", src=os.path.join(extracted_dir, "c", "bin"), dst="bin")
        self.copy(pattern="*", src=os.path.join(extracted_dir, "c", "lib"), dst="lib")
        self.copy(pattern="*", src=os.path.join(extracted_dir, "c", "include"), dst="include")
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.libdirs = []

        bin_path = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH environment variable: %s" % bin_path)
        self.env_info.PATH.append(bin_path)

        self.deps_user_info.perl = os.path.join(self.package_folder, "bin", "perl.exe").replace("\\", "/")
