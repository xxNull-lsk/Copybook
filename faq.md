# Linux下的编译问题

- 安装到/usr/local/bin的问题

    文件：`linux/flutter/CMakeLists.txt`中
    新增：

    ```cmake
    set(CMAKE_INSTALL_PREFIX_INITIALIZED_TO_DEFAULT 1)
    ```



# windows下的编译问题
- 不支持中文
    将文件转为UTF-8 BOM编码格式。
- setlocae问题
    升级开发工具为vs2022 + Windows 10 SDK

- DOWNLOAD_EXTRACT_TIMESTAMP不是批处理命令
    文件：`windows\flutter\ephemeral\.plugin_symlinks\printing\windows\DownloadProject.CMakeLists.cmake.in`中
    删除：

    ```cmake
    DOWNLOAD_EXTRACT_TIMESTAMP true
    ```

# MacOS下遇到的问题
- 编译错误
```bash
    [!] The name of the given podspec `platform_device_id` doesn't match the expected one `platform_device_id_v3
```
`macos/Flutter/ephemeral/.symlinks/plugins/platform_device_id_v3/macos/platform_device_id.podspec`，其中`s.name`改为`platform_device_id_v3`

- 无法访问网络
`macos/Runner/DebugProfile.entitlements`和 `macos/Runner/Release.entitlements`中新增：
```xml
	<key>com.apple.security.network.client</key>
	<true/>
```