// require jquery
//
var FormHelper = (function() {
    function FormValidator(formSelector, bundleHash, submitError, submitSuccess) {
        function errorLog(x) {
            console.error("[FormValidator] " + x);
        }
        $(document).ready(function () {
            function validateOne(selector, validatorHash, errorElemList, parent) {
                var validator = validatorHash.validate,
                    validateFun = validator,
                    errorHandler = validatorHash.error,
                    successHandler = validatorHash.success, 
                    elemArray = $(selector),
                    success = true;

                if (typeof validator === "string") {
                    if (validator === "blank") {
                        validateFun = function (elem) {
                            if (elem.value.trim() === "") {
                                return false;
                            }
                        };
                    } else if (validator === "empty") {
                        validateFun = function (elem) {
                            if (elem.value === "") {
                                return false;
                            }
                        };
                    }
                } else if (validator instanceof RegExp) {
                    validateFun = function (elem) {
                        if (!validator.test(elem.value)) {
                            return false;
                        }
                    };
                } 
                if (validateFun === undefined) {
                    if (!!successHandler)
                        successHandler($(elem));
                    return true;
                }

                for (var idx = 0; idx < elemArray.length; idx++) {
                    var elem = elemArray[idx];
                    var ret = validateFun(elem);
                    if (ret !== undefined && ret !== true) {
                        errorHandler($(elem), ret);
                        errorElemList.push({element: $(elem), errorValue: ret});
                        success = false;
                    } else {
                        if (!!successHandler) {
                            successHandler($(elem));
                        }
                    }
                }
                return success;
            }

            function validateAll (errorElemList) {
                var success = true;
                for (var hashName in bundleHash) {
                    if (bundleHash.hasOwnProperty(hashName)) {
                        var validatorHash = bundleHash[hashName];
                        if (!validateOne(hashName, validatorHash, errorElemList)) {
                            success = false;
                        }
                    }
                }
                return success;
            }

            $(formSelector).submit(function (event) {
                var errorElemList = [];
                if (!validateAll(errorElemList)) {
                    if (!!submitError) {
                        submitError(errorElemList);
                    }
                    event.preventDefault();
                } else {
                    if (!!submitSuccess) {
                        submitSuccess(event);
                    }
                }
            });
            // !-- end of $(document).ready(...)
        });
        function forEachElement(fun) {
            for (var hashName in bundleHash) {
                if (bundleHash.hasOwnProperty(hashName)) {
                    fun($(hashName));
                }
            }
        }
        return {
            disableAll: function () {
                forEachElement(function (elem) {
                    elem.attr("disabled", "");
                });
            },
            enableAll: function () {
                forEachElement(function (elem) {
                    elem.attr("disabled", null);
                });
            }
        };
    }

    return {
        FormValidator: FormValidator
    }
})();
