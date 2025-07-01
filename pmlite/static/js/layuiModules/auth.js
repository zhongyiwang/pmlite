/**
 * 权限认证模块
 * 用于处理JWT认证、权限控制和菜单渲染
 */
layui.define(['layer', 'element'], function (exports){
    const $ = layui.jquery;
    const layer = layui.layer;
    const element = layui.element;

    // Token存储键名
    const TOKEN_KEYS = {
        accessToken: 'jwt_access_token',
        refreshToken: 'jwt_refresh_token'
    }

    // Token工具类
    const TokenUtils = {
        // 解析JWT
        parseToken(token){
            if (!token) return null;
            try {
                const parts = token.split('.');
                if (parts.length !== 3) return null;

                //解码payload
                const payload = JSON.parse(atob(parts[1]));
                return payload;
            } catch (error) {
                console.error('解析JWT失败', error);
                return null;
            }
        },

        // 获取AccessToken
        getAccessToken() {
            return layui.data("system")[TOKEN_KEYS.accessToken];
        },

        // 获取RefreshToken
        getRefreshToken() {
            return layui.data("system")[TOKEN_KEYS.refreshToken]
        },

        //设置JWT
        setTokens(accessToken, refreshToken) {
            layui.data ("system", {
                key: TOKEN_KEYS.accessToken,
                value: accessToken
            });
            if (refreshToken) {
                layui.data ("system", {
                    key: TOKEN_KEYS.refreshToken,
                    value: refreshToken
                });
            };
        },

        // 移除JWT
        removeTokens() {
            layui.data ("system", {
                key: TOKEN_KEYS.accessToken,
                remove: true
            });
            layui.data ("system", {
                key: TOKEN_KEYS.refreshToken,
                remove: true
            })
        },

        // 检查AccessToken是否有效
        isAccessTokenValid(){
            const token = this.getAccessToken();
            if (!token) return false;

            const payload = this.parseToken(token);
            if (!payload) return false;

            // 检查token是否过期(提前5分钟视为过期)
            const currentTime = Date.now() / 1000;
            return payload.exp && payload.exp > (currentTime + 300);
        },

        // 检查RefreshToken是否有效
        isRefreshTokenValid() {
            const token = this.getRefreshToken();
            if (!token) return false;

            const payload = this.parseToken(token);
            if (!payload) return false;

            const currentTime = Date.now() / 1000;
            return payload.exp && payload.exp > currentTime;
        }
    };

    // 权限控制类
    const AuthControl = {
        // 当前用户信息
        userInfo: {},

        // 初始化
        init() {
            const accessToken = TokenUtils.getAccessToken();
            if (!accessToken) return false;

            const payload = TokenUtils.parseToken(accessToken);
            if (payload) {
                this.userInfo = payload;
                return true;
            }
            return false;
        },

        //获取当前用户信息
        getUserInfo() {
            return this.userInfo;
        },

        // 检查用户是否有某个权限
        hasPermission(permission) {
            if (!this.userInfo.permissions || !this.userInfo.permissions.length) {
                return false;
            }

            if (Array.isArray(permission)) {
                // 检查多个权限（满足任意1个即可）
                return permission.some(p => this.userInfo.permissions.includes(p));
            }

            // 检查单个权限
            return this.userInfo.permissions.includes(permission);
        },

        // 根据权限显示/隐藏元素
        controlElementByPermission(elementId, requiredPermission) {
            const element = document.getElementById(elementId);
            if (element && !this.hasPermission(requiredPermission)) {
                element.style.display = 'none';
            }
        },

        // 根据权限渲染菜单
        renderMenu(menuConfig, targetId = 'sidebarMenu') {
            const sidebarMenu = document.getElementById(targetId);
            if (!sidebarMenu) return;

            let menuHtml = '';

            menuConfig.forEach(item => {
                // 如果菜单项需要权限且用户没有该权限，则跳过
                if (item.permission && !this.hasPermission(item.permission)) {
                    return;
                }

                // 生成菜单项HTML
                if (item.children && item.children.length > 0) {
                    // 有子菜单的一级导航
                    let childrenHtml = '';
                    item.children.forEach(child => {
                        if (!child.permission || this.hasPermission(child.permission)) {
                            childrenHtml += `
                                <dd>
                                    <a href="javascript:;" data-url="${child.url}">
                                        <i class="layui-icon ${child.icon || 'layui-icon-file'}"></i>
                                        ${child.title}
                                    </a>
                                </dd>
                            `;
                        }
                    });

                    if (childrenHtml) {
                        // 默认展开二级导航
                        menuHtml += `
                            <li class="layui-nav-item layui-nav-itemed">
                                <a href="javascript:;">
                                    <i class="layui-icon ${item.icon || 'layui-icon-app'}"></i>
                                    ${item.title}
                                    <i class="layui-icon layui-icon-down layui-nav-more"></i>
                                </a>
                                <dl class="layui-nav-child">
                                    ${childrenHtml}
                                </dl>
                            </li>
                        `;
                    }
                } else {
                    // 无子菜单
                    menuHtml += `
                        <li class="layui-nav-item">
                            <a href="javascript:;" data-url="${item.url}">
                                <i class="layui-icon ${item.icon || 'layui-icon-file'}"></i>
                                ${item.title}
                            </a>
                        </li>
                    `;
                }
            });

            sidebarMenu.innerHTML = menuHtml;

            // 绑定菜单点击事件
            this._bindMenuEvents(targetId);

            // 重新渲染导航
            element.render('nav', targetId);
        },

        // 绑定菜单事件
        _bindMenuEvents(targetId) {
            // 一级菜单点击展开/收缩
            $(`#${targetId} > .layui-nav-item > a`).on('click', function (e) {
                const $this = $(this);
                const $navItem = $this.parent();

                // 如有有子菜单
                if ($navItem.find('dl').length > 0) {
                    e.stopPropagation();  // 阻止事件冒泡

                    // 切换展开/收缩状态
                    if ($navItem.hasClass('layui-nav-itemed')) {
                        $navItem.removeClass('layui-nav-itemed');
                    } else {
                        // 关闭其他已展开的菜单
                        // $(`#${targetId} > .layui-nav-item.layui-nav-itemed`).removeClass('layui-nav-itemed');

                        $navItem.addClass('layui-nav-itemed')
                    }
                }
            });

            // 二级菜单点击加载内容
            $(`#${targetId} dl a[data-url]`).on('click', function () {
                const title = $(this).text().trim();
                const url = $(this).attr('data-url');
                const tabId = 'tab_' + url.replace(/[^a-zA-Z0-9]/g, '_');  // 生成唯一的tab ID
                if (url) {
                    // 检查标签是否已打开
                    if ($(`.layui-tab-title li[lay-id="${tabId}"]`).length === 0) {
                        // 新增一个标签页
                        element.tabAdd('mainTabs', {
                            title: title,
                            content: `<iframe src="${url}" frameborder="0" style="width: 100%; height: calc(100vh - 120px);"></iframe>`,
                            id: tabId
                        });
                    }

                    // 切换到指定标签页
                    element.tabChange('mainTabs', tabId)

                    // 高亮当前选中的菜单项
                    $(`#${targetId} dl dd`).removeClass('layui-this');  // 取消其他二级菜单高亮
                    $(`#${targetId} > .layui-nav-item`).removeClass('layui-this');  // 取消其他一级菜单高亮
                    $(this).parent().addClass('layui-this')
                }
            });

            // 无子菜单的一级菜单点击在标签页中打开
            $(`#${targetId} .layui-nav-item > a[data-url]`).on('click', function () {
                const title = $(this).text().trim();
                const url = $(this).attr('data-url');
                const tabId = 'tab_' + url.replace(/[^a-zA-Z0-9]/g, '_');  // 生成唯一的tab ID
                if (url) {
                    // 检查标签是否已打开
                    if ($(`.layui-tab-title li[lay-id="${tabId}"]`).length === 0) {
                        // 新增一个标签页
                        element.tabAdd('mainTabs', {
                            title: title,
                            content: `<iframe src="${url}" frameborder="0" style="width: 100%; height: calc(100vh - 120px);"></iframe>`,
                            id: tabId
                        });
                    }

                    // 切换到指定标签页
                    element.tabChange('mainTabs', tabId)

                    // 高亮当前选中的菜单项
                    $(`#${targetId} > .layui-nav-item`).removeClass('layui-this');  // 取消其他一级菜单高亮
                    $(`#${targetId} dl dd`).removeClass('layui-this');  // 取消其他二级菜单高亮
                    $(this).parent().addClass('layui-this')
                }
            });
        },

        // 登录方法
        login(number, password, callback) {
            const data = {
                number: number,
                password: password
            }
            $.ajax({
                url: '/api/v1/login',
                method: 'POST',
                data: JSON.stringify(data),
                contentType: "application/json",
                success: (res) => {
                    console.log(res)
                    if (res.code === 0 && res.access_token) {
                        // 保存tokens
                        TokenUtils.setTokens(res.access_token, res.refresh_token);
                        this.init();
                        callback(true, res.msg || '登录成功');
                    } else {
                        callback(false, res.msg || '登录失败');
                    }
                },
                error: (err) => {
                    console.log('登录请求失败', err);
                    callback(false, '网络错误，请重试');
                }
            });
        },

        // 登出方法
        logout() {
            TokenUtils.removeTokens();
            layer.msg('已退出登录', {icon: 1});
            setTimeout(() => {
                window.location.href = '/user/login';
            }, 1000);
        },

        // 刷新AccessToken
        refreshToken(callback) {
            if (!TokenUtils.isRefreshTokenValid()) {
                callback(false, '刷新令牌无效，请重新登录');
                return
            }
            const refreshToken = TokenUtils.getRefreshToken()

            $.ajax({
                url: '/api/v1/refresh',
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${refreshToken}`
                },
                success: (res) => {
                    if (res.code === 0 && res.data.access_token) {
                        TokenUtils.setTokens(res.data.access_token, null);
                        this.init()
                        callback(true);
                    } else {
                        // 刷新失败，可能refresh_token已过期
                        TokenUtils.removeTokens();
                        callback(false, res.msg || '刷新令牌已过期，请重新登录');
                    }
                },
                error: (err) => {
                    console.log('刷新token失败：', err);
                    TokenUtils.removeTokens();
                    callback(false, '网络错误，请重新登录');
                }
            });
        },

        // 封装带自动刷新token的API请求
        apiRequest(options) {
            const originalSuccess = options.success;
            const originalError = options.error;

            // 检查access_token有效性
            if (!TokenUtils.isAccessTokenValid()) {
                // access_token无效，重新发送请求
                this.refreshToken((success, message) => {
                    if (success) {
                        // 刷新成功，重新发送请求
                        this._sendApiRequest(options);
                    } else {
                        // 刷新失败，跳转到登录页
                        layui.msg(message || '登录状态已过期', {icon: 2});
                        setTimeout(() => {
                            window.location.href = '/user/login'
                        }, 1500);
                    }
                });
                return
            }

            // access_token有效，直接发送请求
            this._sendApiRequest(options);
        },

        // 发送API请求
        _sendApiRequest(options) {
            const accessToken = TokenUtils.getAccessToken();

            // 添加Authorization头
            options.headers = options.headers || {};
            options.headers['Authorization'] = `Bearer ${accessToken}`;

            //成功回调
            options.success = function (res) {
                if (res.code ===401) {
                    // token无效，尝试栓新
                    AuthControl.refreshToken((success, message) => {
                        if (success) {
                            // 刷新成功，重新发送请求
                            AuthControl._sendApiRequest(options);
                        } else {
                            // 刷新失败，跳转到登录页
                            layui.msg(message || '登录状态已过期', {icon: 2});
                            setTimeout(() => {
                                window.location.href = '/user/login'
                            }, 1500);

                            if (typeof originalError === 'function') {
                                originalError.call(this, res);
                            }
                        }
                    });
                } else {
                    if (typeof originalSuccess === 'function') {
                        originalSuccess.call(this, res);
                    }
                }
            };

            // 错误回调
             options.error = function (res) {
                if (res.status ===401) {
                    // token无效，尝试栓新
                    AuthControl.refreshToken((success, message) => {
                        if (success) {
                            // 刷新成功，重新发送请求
                            AuthControl._sendApiRequest(options);
                        } else {
                            // 刷新失败，跳转到登录页
                            layui.msg(message || '登录状态已过期', {icon: 2});
                            setTimeout(() => {
                                window.location.href = '/user/login'
                            }, 1500);
                        }
                    });
                } else {
                    if (typeof originalError === 'function') {
                        originalError.call(this, err);
                    }
                }
            };

             $.ajax(options);
        }
    };

    // 初始化模块
    const isAuthenticated = AuthControl.init();

    // 导出模块
    exports('auth', {
        isAuthenticated,
        getUserInfo: AuthControl.getUserInfo.bind(AuthControl),
        hasPermission: AuthControl.hasPermission.bind(AuthControl),
        controlElement: AuthControl.controlElementByPermission.bind(AuthControl),
        renderMenu: AuthControl.renderMenu.bind(AuthControl),
        login: AuthControl.login.bind(AuthControl),
        logout: AuthControl.logout.bind(AuthControl),
        refreshToken: AuthControl.refreshToken.bind(AuthControl),
        apiRequest: AuthControl.apiRequest.bind(AuthControl)
    });
});