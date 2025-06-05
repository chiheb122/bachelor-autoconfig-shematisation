#include <pybind11/pybind11.h>
#include <pybind11/stl.h>           // Pour utiliser std::string, std::vector etc.
#include "include/pka2xml.hpp"      // Ton header C++ avec encrypt/decrypt

namespace py = pybind11;

PYBIND11_MODULE(pka2core, m)
{
    m.doc() = "Bindings Python pour le chiffrement et déchiffrement de fichiers Packet Tracer (.pkt / .pka)";

    // 🔓 Déchiffrement (retourne un str décodé, car le contenu est du XML UTF-8)
    m.def("decrypt_pka", [](py::bytes b) {
        std::string input = b;
        std::string result = pka2xml::decrypt_pka(input);
        return py::str(result);  // UTF-8 → str Python
    }, "Déchiffre un fichier .pkt/.pka vers XML");

    // 🔐 Chiffrement (accepte une chaîne binaire, retourne une chaîne binaire)
    m.def("encrypt_pka", [](py::bytes b) {
        std::string input = b;
        std::string encrypted = pka2xml::encrypt_pka(input);
        return py::bytes(encrypted);  // str C++ → bytes Python
    }, "Chiffre un XML en fichier .pkt/.pka");
}
