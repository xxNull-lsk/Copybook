//
//  Generated file. Do not edit.
//

// clang-format off

#include "generated_plugin_registrant.h"

#include <platform_device_id_linux/platform_device_id_linux_plugin.h>
#include <printing/printing_plugin.h>

void fl_register_plugins(FlPluginRegistry* registry) {
  g_autoptr(FlPluginRegistrar) platform_device_id_linux_registrar =
      fl_plugin_registry_get_registrar_for_plugin(registry, "PlatformDeviceIdLinuxPlugin");
  platform_device_id_linux_plugin_register_with_registrar(platform_device_id_linux_registrar);
  g_autoptr(FlPluginRegistrar) printing_registrar =
      fl_plugin_registry_get_registrar_for_plugin(registry, "PrintingPlugin");
  printing_plugin_register_with_registrar(printing_registrar);
}
