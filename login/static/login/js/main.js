$().ready(function () {
    /*浏览器判断与弹窗*/
    var userAgent = navigator.userAgent;
    if (userAgent.indexOf("Chrome") > -1) {
        alert("You are using Chrome or Edge browser.");
    } else if (userAgent.indexOf("Firefox") > -1) {
        alert("You are using Firefox browser.");
    } else if (userAgent.indexOf("Safari") > -1) {
        alert("You are using Safari browser.");
    } else if (userAgent.indexOf("MSIE") > -1 || userAgent.indexOf("Trident") > -1) {
        alert("You are using Internet Explorer browser.");
    } else {
        alert("You are using an unknown browser.");
    }

    //按钮点击事件
    $("#infosub").click(function (){
        var psw=$("#psw").val();
        var email=$("#email").val();
        var fname=$("#fname").val();
        var lname=$("#lname").val();

        //每个input判定
        $(".ifnull").each(function(){
            if($(this).val() === ""){
                $(this).css("border-color", "red"); // 如果为空，则改变边框颜色为红色
            } else {
                $(this).css("border-color", ""); // 如果不为空，恢复默认边框颜色
            }
        });

        if (psw=="" || email=="" || fname=="" || lname==""){
            $(".warn").text("Please fill in the information completely");
        }else{
            $(".warn").text("");
            alert("Create success!")
        }
    })

})


