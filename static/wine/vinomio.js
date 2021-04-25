
'use strict';

function winefetch(){
    console.log("call api!")
}

function sortMeBy(arg, sel, elem, order) {
    var $selector = $(sel),
    $element = $selector.children(elem);
    $element.sort(function(a, b) {
            var an = parseInt(a.getAttribute(arg)),
            bn = parseInt(b.getAttribute(arg));
            if (order == "asc") {
                    if (an > bn)
                    return 1;
                    if (an < bn)
                    return -1;
            } else if (order == "desc") {
                    if (an < bn)
                    return 1;
                    if (an > bn)
                    return -1;
            }
            return 0;
    });
    $element.detach().appendTo($selector);
}

function sortMeBy(arg, sel, elem, order) {
    var $selector = $(sel),
    $element = $selector.children(elem);
    $element.sort(function(a, b) {
            var an = parseInt(a.getAttribute(arg)),
            bn = parseInt(b.getAttribute(arg));
            if (order == "asc") {
                    if (an > bn)
                    return 1;
                    if (an < bn)
                    return -1;
            } else if (order == "desc") {
                    if (an < bn)
                    return 1;
                    if (an > bn)
                    return -1;
            }
            return 0;
    });
    $element.detach().appendTo($selector);
}
function groupBy(objectArray, property) {
    return objectArray.reduce((acc, obj) => {
       const key = obj[property];
       if (!acc[key]) {
          acc[key] = [];
       }
       // Add object to list for given key's value
       acc[key].push(obj);
       return acc;
    }, {});
 }

function toggleSidebarScrollBar()
{
    //alert("action")
};
class Cookies{
    constructor() {}
    static get(name){
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
}
class Slugify{
    constructor() {}
    static get(str){
        str = str.replace(/^\s+|\s+$/g, '');
        // Make the string lowercase
        str = str.toLowerCase();
        // Remove accents, swap ñ for n, etc
        var from = "ÁÄÂÀÃÅČÇĆĎÉĚËÈÊẼĔȆÍÌÎÏŇÑÓÖÒÔÕØŘŔŠŤÚŮÜÙÛÝŸŽáäâàãåčçćďéěëèêẽĕȇíìîïňñóöòôõøðřŕšťúůüùûýÿžþÞĐđßÆa·/_,:;";
        var to   = "AAAAAACCCDEEEEEEEEIIIINNOOOOOORRSTUUUUUYYZaaaaaacccdeeeeeeeeiiiinnooooooorrstuuuuuyyzbBDdBAa------";
        for (var i=0, l=from.length ; i<l ; i++) {
            str = str.replace(new RegExp(from.charAt(i), 'g'), to.charAt(i));
        }
        // Remove invalid chars
        str = str.replace(/[^a-z0-9 -]/g, '') 
        // Collapse whitespace and replace by -
        .replace(/\s+/g, '-') 
        // Collapse dashes
        .replace(/-+/g, '-'); 
        return str;
    }
}

