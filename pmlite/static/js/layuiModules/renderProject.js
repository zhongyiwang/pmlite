
layui.define(['jquery', 'form'], function (exports){
    let $ = layui.jquery;
    let form = layui.form
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
                            if (taskObj && val.name === taskObj.data.project) {
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
        getUsers: function (elementId){
            $.ajax({
                url: "/api/v1/user",
                type: "get",
                async: false,
                success: function (res) {
                    console.log(res.data)
                    let content = '<option value="">负责人（可搜索）</option>'
                    $.each(res.data, function (i, val) {
                        // content += '<option value="' + val.id + '">' + val.name + '</option>'
                        //if (val.parent_id != 0) {
                            if (obj && val.name === obj.data.owner) {
                                content += '<option value="' + val.id + '" selected>' + val.name + '</option>'
                            } else {
                                content += '<option value="' + val.id + '">' + val.name + '</option>'
                            }
                        //}
                    })
                    // console.log(content)
                    let s = $('#owner_id')
                    s.html(content)
                    //console.log(s.html())
                    form.render('select')
                }
            })
        }
    }

    // 输出模块
    exports('renderProject', obj)
})


