#include "api.hpp"

#include <array>
#include <cstdio>
#include <memory>
#include <sstream>
#include <stdexcept>

namespace trevixa {
namespace {

std::string shell_escape(const std::string& in) {
    std::string out{"\""};
    for (char c : in) {
        if (c == '"') {
            out += "\\\"";
        } else {
            out += c;
        }
    }
    out += "\"";
    return out;
}

std::string run_command(std::string command) {
#if !defined(_WIN32)
    command += " 2>&1";
#endif
#if defined(_WIN32)
    FILE* pipe = _popen(command.c_str(), "r");
#else
    FILE* pipe = popen(command.c_str(), "r");
#endif
    if (!pipe) {
        throw std::runtime_error("Failed to start process");
    }

    std::array<char, 1024> buffer{};
    std::ostringstream output;
    while (fgets(buffer.data(), static_cast<int>(buffer.size()), pipe) != nullptr) {
        output << buffer.data();
    }

#if defined(_WIN32)
    const int exit_code = _pclose(pipe);
#else
    const int exit_code = pclose(pipe);
#endif

    if (exit_code != 0) {
        throw std::runtime_error("Command failed with output: " + output.str());
    }

    return output.str();
}

} // namespace

ApiEntrypoint::ApiEntrypoint(std::string python_exe)
    : python_exe_(std::move(python_exe)) {}

std::string ApiEntrypoint::call_python_function(const std::string& function_name,
                                                const std::vector<std::string>& args) const {
    std::ostringstream cmd;
    cmd << python_exe_ << " trevixa/encode/python/main.py --bridge " << shell_escape(function_name);
    for (const auto& arg : args) {
        cmd << ' ' << shell_escape(arg);
    }
    return run_command(cmd.str());
}

std::string ApiEntrypoint::health_check() const {
    return call_python_function("health_check", {});
}

int run_cli_mode(const ApiEntrypoint& api) {
    try {
        const auto result = api.call_python_function("cli_banner", {});
        std::printf("%s", result.c_str());
        return 0;
    } catch (const std::exception& ex) {
        std::fprintf(stderr, "CLI mode error: %s\n", ex.what());
        return 1;
    }
}

int run_gui_mode(const ApiEntrypoint& api, const GuiConfig& cfg) {
    std::ostringstream args;
    args << "model=" << cfg.model << ";"
         << "reasoning=" << cfg.reasoning_strength << ";"
         << "eagerness=" << cfg.eagerness;

    try {
        const auto state = api.call_python_function("gui_state", {args.str()});
        std::printf("Launching Trevixa GUI...\n");
        std::printf("Config: %s\n", state.c_str());
        const auto result = api.call_python_function("launch_gui", {});
        std::printf("GUI session ended: %s\n", result.c_str());
        return 0;
    } catch (const std::exception& ex) {
        std::fprintf(stderr, "GUI mode error: %s\n", ex.what());
        return 1;
    }
}

} // namespace trevixa
