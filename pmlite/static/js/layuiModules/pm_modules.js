
layui.define(['jquery', 'form'], function (exports){
    let $ = layui.jquery;
    let form = layui.form

    // 给默认的ajax请求添加权限
    $.ajaxSetup({
        headers: {
            Authorization: "Bearer " + localStorage.getItem("access_token")
        }
    })


    let obj = {
        getProjects: function (elementId, status, taskObj){
            let url = "/api/v1/project"
            if (status === "uncompleted") {
                url = url + "?status=uncompleted"
                console.log(url)
            }
            $.ajax({
                url: url,
                type: "get",
                async: false,
                success: function (res) {
                    $("#" + elementId).empty()
                    $("#" + elementId).append('<option value="">请选择项目（可搜索）</option>')
                    if(res.data != null && res.data.length != 0){
                        $.each(res.data, function (i, val){
                            if (taskObj && val.name === taskObj.data['project']) {
                                $("#" + elementId).append('<option value="' + val.id + '" selected>' + val.name + '</option>')
                            } else {
                                $("#" + elementId).append('<option value="' + val.id + '">' + val.name + '</option>')
                            }
                        })
                    }
                    form.render('select')
                }
            })
        },
        getUsers: function (elementId, obj, userType, flag){
            let current_user_id  // 定义变量：当前登录用户id
            if (flag) {  // 如果传递该参数，服务器查询获取当前登录用户id
                $.ajax({
                    type: "GET",
                    url: "/api/v1/user/profile",
                    async: false,
                    success: function (res) {
                        if (res.code === 0) {
                            current_user_id = res.data.id
                            console.log('ccccc')
                        }
                    }
                })
                console.log('绑定当前登录用户：', current_user_id)
            }

            $.ajax({
                url: "/api/v1/user",
                type: "get",
                async: false,
                success: function (res) {
                    $("#" + elementId).empty()
                    $("#" + elementId).append('<option value="">请选择用户（可搜索）</option>')
                    if(res.data != null && res.data.length != 0){
                        $.each(res.data, function (i, val) {
                            if (obj && val.name === obj.data[userType]) {
                                $("#" + elementId).append('<option value="' + val.id + '" selected>' + val.name + '</option>')
                            } else if (current_user_id && current_user_id == val.id) {

                                $("#" + elementId).append('<option value="' + val.id + '" selected>' + val.name + '</option>')
                            } else {
                                $("#" + elementId).append('<option value="' + val.id + '">' + val.name + '</option>')
                            }
                        })
                    }
                    form.render('select')
                }
            })
        }
    }

    // 输出模块
    exports('pmlite', obj)
})

