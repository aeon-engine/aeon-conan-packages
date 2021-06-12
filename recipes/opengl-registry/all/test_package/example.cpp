#include <KHR/khrplatform.h>
#include "xml_paths.h"
#include <filesystem>
#include <iostream>

int main()
{
    const auto gl_exists = std::filesystem::exists(OPENGL_XML_REGISTRY_PATH "/gl.xml");
    const auto glx_exists = std::filesystem::exists(OPENGL_XML_REGISTRY_PATH "/glx.xml");
    const auto wgl_exists = std::filesystem::exists(OPENGL_XML_REGISTRY_PATH "/wgl.xml");

    if (!gl_exists || !glx_exists || !wgl_exists)
    {
        std::cerr << "Expected XML files don't exist.\n";
        return 1;
    }

    std::cout << "Package ok.\n";
    return 0;
}
