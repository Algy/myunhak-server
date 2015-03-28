(function () {
    var emailRegex = /^(([^<>()[\]\\.,;:\s@"]+(\.[^<>()[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
    var phoneRegex = /^[0-9]{2,3}-[0-9]{3,4}-[0-9]{3,4}$/;

    // XXX: group validation

    function getGroupParent(elem) {
        function iter(elem) {
            if (!!elem) {
               if (elem.hasClass("form-group")) {
                   return elem;
               } else {
                   return iter(elem.parent());
               }
            } else
                return null;
        }
        return iter(elem.parent());
    }

    function addErrorMsg (inputElem, msg) {
        var parent = inputElem.parent();
        var groupParent = getGroupParent(inputElem);

        if (!!groupParent) groupParent.addClass("has-error");
        var oldMsgElem = parent.find("[data-errmsg-sig]");
        
        if (oldMsgElem.length == 0) {
            var newTag = $("<div data-errmsg-sig class=\"form-error-span\"></div>");
            newTag.text(msg);
            parent.append(newTag);
        } else {
            oldMsgElem.text(msg);
        }
    }
    function removeErrorMsg (inputElem) {
        var parent = inputElem.parent();
        var groupParent = getGroupParent(inputElem);

        if (!!groupParent) groupParent.removeClass("has-error");
        var oldMsgElem = parent.find("[data-errmsg-sig]");
        oldMsgElem.remove();
    }


    $(document).ready(function() {
        // initialize alert bar
        $(".form-error-alert").hide();


        // install the form validater hook
        var cond = {};
        var nonblankList = [
            ["#submitee [name=name]", "이름을"],
            ["#submitee [name=grade]", "학년을"],
            ["#submitee [name=class]", "반을"],
            ["#submitee [name=desired-date]", "입실 신청 날짜와 시간을"],
            ["#submitee [name=middle-school]", "출신 중학교를"],
            ["#submitee [name=religion]", "종교를"],
            ["#submitee [name=address]", "주소를"],
            ["#submitee [name=desired-univ1]", "희망대학 1순위를"],
            ["#submitee [name=desired-univ2]", "희망대학 2순위를"],
            ["#submitee [name=desired-univ3]", "희망대학 3순위를"],
            ["#submitee [name=desired-job1]", "희망직업 1순위를"],
            ["#submitee [name=desired-job2]", "희망직업 2순위를"],
            ["#submitee [name=desired-job3]", "희망직업 3순위를"]];

        for (var idx = 0; idx < nonblankList.length; idx++) {
            (function () {
                var nonblankSpec = nonblankList[idx];
                var selector = nonblankSpec[0];
                var desc = nonblankSpec[1];
                cond[selector] = {
                    validate: "blank",
                    error: function (elem) {
                        addErrorMsg(elem, desc + " 입력해주세요");
                    },
                    success: removeErrorMsg
                };
            })();
        }


        cond["#submitee [name=email]"] = {
            validate: emailRegex,
            error: function (elem) {
                if (elem.value === "") {
                    addErrorMsg(elem, "이메일을 입력해주세요");
                } else {
                    addErrorMsg(elem, "이메일 형식이 잘못되었습니다");
                }
            },
            success: removeErrorMsg
        };

        cond["#submitee [name=phone]"] = {
            validate: phoneRegex,
            error: function (elem) {
                if (elem.value === "") {
                    addErrorMsg(elem, "핸드폰 번호를 입력해주세요");
                } else {
                    addErrorMsg(elem, "핸드폰 번호를 잘못 입력하셨습니다");
                }
            },
            success: removeErrorMsg
        };

        FormHelper.FormValidator("#submitee", cond, function (errors) {
            // $(".form-error-alert").fadeIn();
            var elemOffsetTop = errors[0].element.offset().top;
            $("body").animate({
                scrollTop: elemOffsetTop - 80,
            }, 200);
        });
        $("#submit-btn").click(function () {
            $("#submitee").submit();
        });
    });
})();

