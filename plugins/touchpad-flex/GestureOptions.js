.pragma library
var ids = ["pinch3In", "pinch3Out", "pinch5In", "pinch5Out", "tap5", "hold4", "hold5", "edgeTop", "edgeBottom", "swipe4UpLeft", "swipe4UpRight", "swipe4DownLeft", "swipe4DownRight", "swipe5Left", "swipe5Right", "swipe5Up", "swipe5Down", "swipe5UpLeft", "swipe5UpRight", "swipe5DownLeft", "swipe5DownRight"];
function label(id, russian) {
    var names = {pinch3In: ["Щипок 3 пальцами", "Three-finger pinch"], pinch3Out: ["Развести 3 пальца", "Three-finger spread"], pinch5In: ["Щипок 5 пальцами", "Five-finger pinch"], pinch5Out: ["Развести 5 пальцев", "Five-finger spread"], tap5: ["Касание 5 пальцами", "Five-finger tap"], hold4: ["Удержать 4 пальца", "Four-finger hold"], hold5: ["Удержать 5 пальцев", "Five-finger hold"], edgeTop: ["От верхнего края", "From the top edge"], edgeBottom: ["От нижнего края", "From the bottom edge"]};
    if (names[id]) return names[id][russian ? 0 : 1];
    var m = /^swipe([45])(.*)$/.exec(id);
    var dirs = {Left: ["влево", "left"], Right: ["вправо", "right"], Up: ["вверх", "up"], Down: ["вниз", "down"], UpLeft: ["вверх-влево", "up-left"], UpRight: ["вверх-вправо", "up-right"], DownLeft: ["вниз-влево", "down-left"], DownRight: ["вниз-вправо", "down-right"]};
    return m ? m[1] + (russian ? " пальца: " : " fingers: ") + dirs[m[2]][russian ? 0 : 1] : id;
}
var thresholds = [
    {key: "swipeMm", ru: "Дистанция свайпа", en: "Swipe distance", def: 22, min: 5, max: 80, step: 1, suffix: " mm"},
    {key: "pinchRatio", ru: "Порог щипка", en: "Pinch ratio", def: 0.6, min: 0.25, max: 0.9, step: 0.05, suffix: ""},
    {key: "tapMs", ru: "Длительность касания", en: "Tap duration", def: 260, min: 100, max: 500, step: 10, suffix: " ms"},
    {key: "holdMs", ru: "Длительность удержания", en: "Hold duration", def: 650, min: 300, max: 2000, step: 50, suffix: " ms"},
    {key: "motionMm", ru: "Допустимое движение при касании", en: "Tap movement tolerance", def: 3.5, min: 1, max: 10, step: 0.5, suffix: " mm"},
    {key: "edgeZone", ru: "Зона края (доля высоты)", en: "Edge zone (fraction of height)", def: 0.04, min: 0.01, max: 0.15, step: 0.01, suffix: ""},
    {key: "edgeTravel", ru: "Дистанция от края (доля высоты)", en: "Edge travel (fraction of height)", def: 0.15, min: 0.05, max: 0.4, step: 0.01, suffix: ""},
    {key: "cooldownMs", ru: "Пауза между срабатываниями", en: "Gesture cooldown", def: 350, min: 100, max: 2000, step: 50, suffix: " ms"}
];
