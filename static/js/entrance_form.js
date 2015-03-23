(function () {
    function makeCheckBlank(fieldname) {
        function checkBlank(val) {
            if (val !== "") {
                return fieldname + " 입력해주세요."
            } else {
                return null;
            }
        }
        return checkBlank;
    }

    var emailRegex = /^(([^<>()[\]\\.,;:\s@"]+(\.[^<>()[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;

    function checkEmailField (val) {
        if (val === "") {
            return "이메일을 입력해주세요."
        } else if (!emailRegex.test(val)) {
            return "올바른 이메일 형식이 아닙니다.";
        } else {
            return null;
        }
    }


    function makeFr() {
        $("<span class=\"help-block\"></div>")
    }



    $(document).ready(function () {
        $("#submit-btn").click(function () {
            $("#submitee").submit();
            /*
            $("")
            $("#html, body").animate({
                scrollTop: $("#submitee").offset().top
            }, 200);
            */
        });
    });
})();

