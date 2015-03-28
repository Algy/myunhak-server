// require jquery
//
var FormHelper = (function() {
    function FormValidator(formSelector, bundleHash, submitError) {
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

                if (validateFun === undefined)
                    return true;

                for (var idx = 0; idx < elemArray.length; idx++) {
                    var elem = elemArray[idx];
                    var ret = validateFun(elem);
                    if (ret !== undefined && ret !== true) {
                        errorHandler($(elem), ret);
                        errorElemList.push({element: $(elem), errorValue: ret});
                        success = false;
                    } else {
                        successHandler($(elem));
                    }
                }
                return success;
            }

            function validateAll () {
                var success = true;
                var errorElemList = [];
                for (var hashName in bundleHash) {
                    if (bundleHash.hasOwnProperty(hashName)) {
                        console.log(hashName);
                        var validatorHash = bundleHash[hashName];
                        if (!validateOne(hashName, validatorHash, errorElemList)) {
                            success = false;
                        }
                    }
                }
                if (!success && !!submitError) {
                    submitError(errorElemList);
                }
                return success;
            }

            $(formSelector).submit(function (event) {
                if (!validateAll()) {
                    event.preventDefault();
                }
            });
        });
    }

    return {
        FormValidator: FormValidator
    }
})();
