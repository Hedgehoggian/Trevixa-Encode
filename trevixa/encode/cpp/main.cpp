#include "api.hpp"

#include <iostream>
#include <string>

int main(int argc, char** argv) {
    trevixa::ApiEntrypoint api{"python"};

    std::string mode = "--gui";
    if (argc > 1) {
        mode = argv[1];
    }

    if (mode == "--cli") {
        return trevixa::run_cli_mode(api);
    }

    if (mode == "--gui") {
        trevixa::GuiConfig cfg{};
        if (argc > 2) cfg.model = argv[2];
        if (argc > 3) cfg.reasoning_strength = argv[3];
        if (argc > 4) cfg.eagerness = argv[4];
        return trevixa::run_gui_mode(api, cfg);
    }

    if (mode == "--health") {
        std::cout << api.health_check() << '\n';
        return 0;
    }

    std::cerr << "Usage: trevixa-encode [--gui|--cli|--health] [model reasoning eagerness]\n";
    return 1;
}
