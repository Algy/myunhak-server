(function () {
    var emailRegex = /^(([^<>()[\]\\.,;:\s@"]+(\.[^<>()[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
    var phoneRegex = /^[0-9]{2,3}-[0-9]{3,4}-[0-9]{3,4}$/;

    function scrollTo(element, duration) {
        duration = duration || 200;
        var elemOffsetTop = element.offset().top;
        $("body").animate({
            scrollTop: elemOffsetTop - 80,
        }, 200);
    }

    var alertIdAcc = 0;
    function oneshotAlertMessage(msg) {
        alertIdAcc += 1;
        var oneshotId = 'alert-banner-' + String(alertIdAcc);
        var template = '<div id="' + oneshotId +
                       '" class="alert alert-danger form-error-alert" role="alert" style="display: none;">' +
                       '    <span class="glyphicon glyphicon-exclamation-sign"></span>' +
                       '    <span class="content">' + msg + '</span>' +
                       '</div>';
        var compiledTemplate = $(template);
        $("#alert-wrapper").append(compiledTemplate);
        $("#" + oneshotId).slideDown();
        console.log(compiledTemplate);
        setTimeout(function () {
            var elem = $("#" + oneshotId);
            elem.slideUp({complete: elem.remove});
        }, 6000);
    }
    function removeAlerts() {
        $("#alert-wrapper .alert").slideUp({
            complete: function () {
                $("#alert-wrapper").empty();
            }
        });
    }




    // XXX: group validation
    function submitButton() {
    }

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
        // install a light checkbox hook
        $("#motive-etc-checkbox").click(function () {
            var elem = $("#submitee [name=motive-etc-content]");
            if (!this.checked) {
                elem.attr("disabled", "disabled");
                elem.attr("placeholder", "");
                elem.val("");
            } else {
                elem.attr("disabled", null);
                elem.attr("placeholder", "동기를 입력해주세요");
            }
        });

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

        cond["#submitee [name=motive-etc-content]"] = {
            validate: function (elem) {
                if ($("#motive-etc-checkbox:checked").length > 0) {
                    if (elem.value.trim() === "") {
                        return false;
                    }
                }
            },
            error: function (elem) {
                addErrorMsg(elem, "동기를 입력해주세요");
            },
            success: removeErrorMsg
        };


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

        var condNone = [
            "#submitee [name=hobby]",
            "#submitee [name=healthy]",
            "#submitee [name=fam-rel]",
            "#submitee [name=fam-name]",
            "#submitee [name=fam-age]",
            "#submitee [name=fam-scolarship]",
            "#submitee [name=fam-job]",
            "#submitee [name=fam-phone]",
            "#submitee [name=inschoolrel-grade]",
            "#submitee [name=inschoolrel-class]",
            "#submitee [name=inschoolrel-name]",
            "#submitee [name=outschoolrel-phone]",
            "#submitee [name=outschoolrel-school]",
            "#submitee [name=outschoolrel-name]",
            "#submitee [name=worry]",
            "#submitee [name=private-lesson]",
            "#submitee [name=note]"
        ];

        for (var idx = 0; idx < condNone.length; idx++) {
            cond[condNone[idx]] = {};
        }

        var validator = FormHelper.FormValidator("#submitee", cond, function (errors) {
            scrollTo(errors[0].element);
        }, function (event) {
            // success
            event.preventDefault();
            submitForm();
        });
        $("#submit-btn").click(function () {
            $("#submitee").submit();
        });

        function startSubmitingState (ajaxContr) {
            // mutation chains for views
            
            var backBtn = $("#back-btn");
            backBtn.attr("disabled", null);
            backBtn.show();
            backBtn.off("click");
            backBtn.click(function () {
                ajaxContr.cancel();
                $("#back-btn").attr("disabled", "");
            });

            
            var submitee = $("#submitee");
            // validator.disableAll();
            submitee.hide();
            $("#submit-progress-img-wrapper").fadeIn();
            $("#submit-btn").attr("disabled", "");
        }

        function endSubmitingState () {
            $("#back-btn").hide();
        }


        function startFormState () {
            $("#submit-success-wrapper").hide();
            $("#submit-progress-img-wrapper").hide();
            $("#back-btn").hide();
            $("#main-page-btn").hide();
            $("#submit-btn").show();

            var submitee = $("#submitee");
            submitee.show();
            // validator.enableAll();
            $("#submitee").show();
            $("#submit-btn").attr("disabled", null);

        }

        function endFormState () {
            grecaptcha.reset();
        }

        function startSuccessState () {
            $("#submit-success-wrapper").show();
            $("#submit-progress-img-wrapper").hide();
            $("#back-btn").hide();
            $("#submit-btn").hide();
            $("#main-page-btn").show();
        }

        function submitForm() {
            var submitee = $("#submitee");
            // AJAX
            var ajaxContr = (function () {
                var canceled = false;
                var xhr = $.ajax({
                    type: "POST",
                    url: "/rest/entrance",
                    data: submitee.serialize(),
                    dataType: "json",
                    timeout: 10000,
                    success: submitSuccess,
                    error: function (xhr, reason) {
                        if (reason === "timeout") {
                            oneshotAlertMessage("응답시간이 초과되었습니다. 다시 시도해주세요.");
                        } else if (reason === "error") {
                            oneshotAlertMessage("제출하는데 오류가 발생하였습니다.");
                        } else if (reason === "abort") {
                        } else {
                            // unknown error
                            oneshotAlertMessage("예기치 못한 오류가 발생하였습니다. 다시 시도해주세요.");
                        }
                        endSubmitingState();
                        startFormState();
                    }
                });
                return {
                    cancel: function () {
                        xhr.abort();
                    }
                };
            })();
            endFormState();
            startSubmitingState(ajaxContr);
        }

        function submitSuccess(result) {
            if (!!result.success) {
                endSubmitingState();
                startSuccessState();
            } else {
                oneshotAlertMessage(result.error_msg);

                endSubmitingState();
                startFormState();
                if (result.error_reason === "recaptcha") {
                    scrollTo($("#recaptcha"), 200);
                }
            }
        }
        startFormState(); // The first state: FormState

    });
})();

