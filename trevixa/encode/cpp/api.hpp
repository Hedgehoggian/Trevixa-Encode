#pragma once

#include <string>
#include <vector>

namespace trevixa {

struct GuiConfig {
    std::string model{"Trevixa Encode Alpha v0.1.0"};
    std::string reasoning_strength{"balanced"};
    std::string eagerness{"normal"};
};

class ApiEntrypoint {
public:
    explicit ApiEntrypoint(std::string python_exe = "python");
    std::string call_python_function(const std::string& function_name,
                                     const std::vector<std::string>& args) const;
    std::string health_check() const;
private:
    std::string python_exe_;
};

int run_cli_mode(const ApiEntrypoint& api);
int run_gui_mode(const ApiEntrypoint& api, const GuiConfig& cfg);

} // namespace trevixa
