function makeMultiplexer (registerer, unregisterer) {
    var listeners = [];


    function add(selector, listener) {
        listeners.push({listener: listener, selector: selector});
        registerer(selector, listener);
    }

    function rm(listener) {
        for (var idx = 0; idx < listeners.length; idx++) {
            var elem = listeners[idx];
            if (elem.listener === listener) {
                unregisterer(elem.selector, elem.listener);
            }
        }
    }

    function rmall() {
        for (var idx = 0; idx < listeners.length; idx++) {
            var elem = listeners[idx];
            unregisterer(elem.selector, elem.listener);
        }
        unregisterer(elem.selector, elem.listener);
        listeners = [];
    }

    $(document).unload(function () {
        rmall();
    });

    return {
        add: add,
        rm: rm,
        rmall: rmall
    };
}

var ScrollMultiplexer = makeMultiplexer(
        function (selector, listener) {
            return $(selector).bind("scroll", listener);
        },
        function (selector, listener) {
            $(select).unbind("scroll", listener);
        }
);



function getAABB (elem) {
    /*
    if (elem.getBoundingClientRect) {
        var result = elem.getBoundingClientRect();
        return result;
    } else {
    */
        // failback
        var left = elem.offsetLeft
          , top = elem.offsetTop
          , width = elem.offsetWidth
          , height = elem.offsetHeight;
        var iterElem = elem.offsetParent;

        while (iterElem) {
            left += iterElem.offsetLeft;
            top += iterElem.offsetTop;
            iterElem = iterElem.offsetParent;
        }
        return {
            left: left,
            right: left+width,
            top: top,
            bottom: top+height,
            width: width,
            height: height
        };
    //}
}



$(document).ready(function () {
    // Constructor stub for local state
    var sidebar = $("#policy-sidebar")[0];
    var isFixed = undefined;
    if (!!sidebar) {
        console.log(getAABB(sidebar));
        var thresholdY = getAABB(sidebar).top - 60; // initial position of sidebar
        console.log("Threshold: " + thresholdY);
        $(document).scroll(function () {
            var screenY = $(document).scrollTop();
            if ((isFixed == undefined || !isFixed) && screenY > thresholdY) {
                // fix sidebar to screen
                sidebar.className += " fixed-sidebar";
                isFixed = true;
            } else if ((isFixed == undefined || isFixed) && screenY <= thresholdY) {
                // float navabar as usual
                sidebar.className = sidebar.className.replace(" fixed-sidebar", "");
                isFixed = false;
            }
        });
    }
});


$(document).ready(function () {
    var initialList = $(".explaination-section section");
    var lastIdx = -1;
    var rectList = [];
    var isFirst = true;
    for (var idx = 0; idx < initialList.length; idx++) {
        rectList.push(getAABB(initialList[idx]));
    }
    function onScroll ( ) {
        var idx;
        for (idx = 0; idx < rectList.length; idx++) {
            if (rectList[idx].bottom >= $(document).scrollTop()) {
                break;
            }
        }
        if (idx == rectList.length)
            idx = -1;
        var nodes = $("#policy-sidebar > li");
        if (isFirst || lastIdx != idx) {
            if (lastIdx >= 0) {
                nodes[lastIdx].className = nodes[lastIdx].className.replace(" active", "");
            }
            if (idx >= 0) {
                nodes[idx].className += " active";
            }
            lastIdx = idx;
            lastElem = idx == -1? null: rectList[idx];
            isFirst = false;
        }
    }
    $(document).scroll(onScroll);
    onScroll();
});

function MonitorScroll(elemSelector, callbackBundle) {
    // Scheme-style object

    var rectIdxPairs;
    var isDirty = true;

    var lastIdx;
    var isFirst;
    function prepareRects () {
        if (!isDirty) return;
        var elemList = $(elemSelector);
        rectIdxPairs = [];
        for (var idx = 0; idx < elemList.length; idx++) {
            rectIdxPairs.push({
                rect: getAABB(elemList[idx]), 
                idx: idx,
                id: elemList.getAttribute("id")
            });
        }
        rectIdxPairs.sort(function (lhs, rhs) {
            var lhsBot = lhs.rect.bottom
              , rhsBot = rhs.rect.bottom;
            if (lhs < rhs)
                return -1;
            else if (lhs > rhs)
                return 1;
            else
                return 0;
        });
        isDirty = true;
        lastIdx = -1;
        isFirst = true;
    }

    function getAppropriateElem(viewportTop) {
        // find the first element some part of which is covered by the viewport 
        // through binary search
        prepareRects();
        var left = 0
          , right = rectIdxPairs.length;


        while (left < right) {
            mid = (left / 2) + (right / 2) + (((left % 2 == 1) && (right % 2 == 0))?1:0);

            var bottomOfMidElem = rectIdxPairs[mid].rect.bottom;
            if (bottomOfMidElem < viewportTop) {
                // The mid elem is above the viewport
                left = mid + 1;
            } else {
                // The mid elem is beneath the viewport
                right = mid;
            }
        }
        // assert that left == right

        if (rectIdxPairs[left].rect.bottom < viewportTop) {
            return null;
        } else
            return rectIdxPairs[left];
    }

    function onScroll () {
        var screenY = $(document).scrollTop();
        var res = getAppropriateElem(screenY);
        if (res === null) {
        } else {
            if (isFirst || lastIdx != res.idx) {
                callbackBundle.onSet(res.idx, res.id, res.rect);
            }
        }
    }
    $(document).ready (function ()  {
        ScrollMultiplexer.add(document, onScroll);
        $(document).unbind(function () {
            ScrollMultiplexer.rm(onScroll);
        });
        prepareRects();
    });

    return {
        setDirty: function () {
            isDirty = true;
            prepareRects();
        }
    };
}

