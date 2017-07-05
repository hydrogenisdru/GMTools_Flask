/**
 * Created by zouyang on 2017/6/26.
 */
function isCurrency(id) {
    return 0 <= id && id < 100;
}


function isItem(id) {
    return 100 <= id && id < 100000
}


function isHero(id) {
    return 100000 <= id && id < 110000
}


function isGun(id) {
    return 110000 <= id && id < 120000
}


function isHeroSkin(id) {
    return 10000000 <= id && id < 11000000
}


function isGunSkin(id) {
    return 11000000 <= id && id < 12000000
}


function isMonsterGunSkin(id) {
    return 12000000 <= id && id < 13000000;
}

function isDate(str) {
    if (str.length != 0) {
        var reg = /^(\d{1,4})(-|\/)(\d{1,2})\2(\d{1,2})$/;
        var r = str.match(reg);
        if (r != null)
            return true;
    }
    return false;
}
