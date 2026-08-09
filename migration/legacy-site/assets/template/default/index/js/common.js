//监听加载状态改变
document.onreadystatechange = completeLoading;
//加载状态为complete时移除loading效果
function completeLoading() {
    $("#loading").css({ display: "block" });
    document.body.style.cssText = "overflow: hidden";    
    if (document.readyState == "complete") {
        $("#loading").fadeOut(200);
        document.body.style.cssText = "overflow: auto";
    }   
}

function $2(o) { return document.getElementById(o); }

var banobj = null;
var kvindex = 1;
var kvcount = 1;
var kvtime = 5000;
var _timeout = null;
function SetKv(k) {
    if (k == kvindex || kvcount == 1)
        return;

    clearTimeout(_timeout);
    if (k == 0)
        k = kvindex + 1;
    else if (k == -1)
        k = kvindex - 1;
    if (k > kvcount)
        k = 1;
    else if (k < 1)
        k = kvcount;
    var cindex = kvindex - 1;
    banobj.find(".banbtns a:eq(" + cindex + ")").removeClass("cur");
    banobj.find("ul li:eq(" + cindex + ")").animate({ opacity: 'hide' }, "slow");
    kvindex = k;
    cindex = k - 1;
    banobj.find(".banbtns a:eq(" + cindex + ")").addClass("cur");
    banobj.find("ul li:eq(" + cindex + ")").animate({ opacity: 'show' }, "slow");
    _timeout = setInterval("SetKv(0)", kvtime);
}

function initBan(_banobj) {
    clearTimeout(_timeout);
    banobj = _banobj;
    kvindex = 1;
    kvcount = banobj.find("ul").children("li").length;
    banobj.find("ul li").each(function () {
        if (banobj.find("ul li").index(this) == 0)
            $(this).show();
        else
            $(this).hide();
    });
    var banbtns = "";
    for (var i = 1; i <= kvcount; i++)
        banbtns += "<a href=\"javascript:void(0)\" onClick=\"SetKv(" + i + ")\"></a>";
    banobj.find(".banbtns").html(banbtns);
    setTimeout(function () {
        banobj.find(".banbtns a").each(function () {
            if (banobj.find(".banbtns a").index(this) == 0) {
                if (!$(this).hasClass("cur"))
                    $(this).addClass("cur");
            }
            else {
                if ($(this).hasClass("cur"))
                    $(this).removeClass("cur");
            }
        });
        _timeout = setInterval("SetKv(0)", kvtime);
    }, 100);
}

function initMenu() {
    $(".menulist a").mouseover(function () {
        var objname = $(this).attr("id").replace("menu_", "");
        if ($("#smenu_" + objname).length > 0) {
            if (!$(this).hasClass('cor'))
                $(this).addClass('cor');
            if (!$("#smenu_" + objname).is(":visible"))
                $("#smenu_" + objname).show();
        }
    });

    $(".menulist a").mouseout(function () {
        var objname = $(this).attr("id").replace("menu_", "");
        if ($("#smenu_" + objname).length > 0) {
            if ($(this).hasClass('cor'))
                $(this).removeClass('cor');
            if ($("#smenu_" + objname).is(":visible"))
                $("#smenu_" + objname).hide();
        }
    });

    $(".smenubox").mouseover(function () {
        var objname = $(this).attr("id").replace("smenu_", "");
        if (!$("#menu_" + objname).hasClass('cor'))
            $("#menu_" + objname).addClass('cor');
        if (!$(this).is(":visible"))
            $(this).show();
    });

    $(".smenubox").mouseout(function () {
        var objname = $(this).attr("id").replace("smenu_", "");
        if ($("#menu_" + objname).hasClass('cor'))
            $("#menu_" + objname).removeClass('cor');
        if ($(this).is(":visible"))
            $(this).hide();
    });
}

function initSeries() {
    $(".index_seriesbox .btns a").click(function () {
        var cindex = $(this).index();
        var plink = $(this).attr("plink");
        var bobj = $(this).parent().parent().parent();
        var oindex = 0;
        bobj.find(".btns a").each(function () {
            if ($(this).hasClass("cur"))
                oindex = $(this).index();
        });
        bobj.find(".btns a:eq(" + oindex + ")").removeClass("cur");
        bobj.find("ul li:eq(" + oindex + ")").animate({ opacity: 'hide' }, "slow");

        bobj.find(".btns a:eq(" + cindex + ")").addClass("cur");
        bobj.find("ul li:eq(" + cindex + ")").animate({ opacity: 'show' }, "slow");

        bobj.find(".dbtn").attr("href", plink);
    });
}

function ShowSearch() {
    if (!$("#smenu_search").is(":visible"))
        $("#smenu_search").show();
    else
        $("#smenu_search").hide();
}

//收藏本站
function AddFavorite(title, url) {
    try {
        window.external.addFavorite(url, title);
    }
    catch (e) {
        try {
            window.sidebar.addPanel(title, url, "");
        }
        catch (e) {
            alert("抱歉，您所使用的浏览器无法完成此操作。\n\n加入收藏失败，请使用Ctrl+D进行添加");
        }
    }
}

//验证手机
function ValidateMobile(mobile)
{
    var a = /^((\(\d{3}\))|(\d{3}\-))?13\d{9}|15\d{9}|18\d{9}$/ ;
    if(mobile.length!=11||!mobile.match(a)){
        return false;
    }
    return true;
}

//验证email
function ValidateEmail(j)
{
	var emailReg=/^([a-zA-Z0-9]+[_|\_|\.]?)*[a-zA-Z0-9]+@([a-zA-Z0-9]+[_|\_|\.|\-]?)*[a-zA-Z0-9]+\.[a-zA-Z]{2,3}$/;
	return emailReg.test(j);
}

//验证金额
function isDigit(object,value)
{
	var patrn=/^-?\d+\.{0,}\d{0,}$/;
	if (!patrn.exec(value))
	{
		object.value = "";
	}
}

function IsChecked(ObjName)
{
	var list = document.getElementsByName(ObjName);
	var returnVal=false;
	for(var i=0;i<list.length;i++)
	{
		if(list[i].checked)
		{
			returnVal = true;
			break;
		}
	}
	return returnVal;
}

function CheckedAllbyChk(obj, chkname) {
    $('input[name="pchk"]').each(function () {
        if (!$(this).attr("disabled"))
            $(this).attr("checked", $(obj).attr("checked") == "checked" ? true : false);
    });
}

//限制字数
function textCounterN(field, countfield, maxlimit) {	
	var _con = $("#"+field).val();
	if (_con.length > maxlimit) 
	    $("#"+field).val(_con.substring(0,maxlimit));
	else 
	    $("#"+countfield).html(maxlimit - _con.length);
}

//只能输入数字和小数点
function KeyPress(objTR)
{ 
    var txtval=objTR.value;  
    var l=objTR.value.length;
    var key = event.keyCode;
    if((key < 48||key > 57)&&key != 46)
    {  
        event.keyCode = 0;
    }    
    else
    {
        if(key == 46)
        {
            if(txtval.indexOf(".") != -1||txtval.length == 0)
            {
                event.keyCode = 0;
            }
        }
    }
}

//获取浏览器竖向滚动条宽度
function getScrollWidth() {
    var noScroll, scroll, oDiv = document.createElement("DIV");
    oDiv.style.cssText = "position:absolute; top:-1000px; width:100px; height:100px; overflow:hidden;";
    noScroll = document.body.appendChild(oDiv).clientWidth;
    oDiv.style.overflowY = "scroll";
    scroll = oDiv.clientWidth;
    document.body.removeChild(oDiv);
    return noScroll-scroll;
}

//判断页面是否滚动到底部
function reachBottom() {
    var scrollTop = 0;
    var clientHeight = 0;
    var scrollHeight = 0;
    if (document.documentElement && document.documentElement.scrollTop) {
        scrollTop = document.documentElement.scrollTop;
    } else if (document.body) {
        scrollTop = document.body.scrollTop;
    }
    if (document.body.clientHeight && document.documentElement.clientHeight) {
        clientHeight = (document.body.clientHeight < document.documentElement.clientHeight) ? document.body.clientHeight : document.documentElement.clientHeight;
    } else {
        clientHeight = (document.body.clientHeight > document.documentElement.clientHeight) ? document.body.clientHeight : document.documentElement.clientHeight;
    }
    scrollHeight = Math.max(document.body.scrollHeight, document.documentElement.scrollHeight);
    if (scrollTop + clientHeight == scrollHeight) {
        return true;
    } else {
        return false;
    }
}

//刷新验证码
function refreshValideCode(Img, Code) {
    $("#" + Img).attr("src", Code + Math.random());
}

function GoTo(_top) {
    $('html, body').animate({
        scrollTop: _top
    }, 500);
}

function ShowAreas() {

}