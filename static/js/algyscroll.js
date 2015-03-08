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
    for (var idx = 0; idx < initialList.length; idx++) {
        console.log("[" + idx + "].top: " + rectList[idx].top);
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
