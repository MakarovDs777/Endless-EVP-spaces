# Endless-illusory-spaces
Перепишите программу в которой игрок от первого лица будет находится в пространстве тонкого мира уберите шум Перлина, и замените его пространством тонкого мира это такое пространство в которой каждая область пространства разделяется на кубическую сетку 2x2 метр где каждая точка в этой кубической сетке является градиентом в котором каждый градиент имеет имеет параметр RGB ввиде red, green, blue, alpha, где red это степень красного цвета, green степень зеленого чем ближе он к одному 1 тем зеленее он, blue степень синего чем ближе он к одному 1 тем синее он, и alpha соответственно степень светлости этого цвета чем ближе он к одному 1 тем светлее он а если ближе к 0 то он чернее, и каждый из этих параметров имеет диапазон от 0 <= 1 и за каждую секунду времени в нём генерируется случайное значение вещественного числа все эти параметры складывается с дург другом образуя конечный цвет, и этот параметр ввиде RGB является цветом этого градиента, и соответственно каждый градиент имеет случайный диаметр от 0 до 5 метров постоянно появляется и исчезает словно квантовая флуктуация, и при этом сама кубическая сетка невидима игроку, и сам игрок может двигаться с помощью клавиш w,a,s,d и так же направлением мышки двигать камеру, и соответственно само пространство бесконечно процедурно генерируется по мере движения в этом пространстве игрока. 

Если вы до сих пор не поняли суть идеи программного кода заключатся в том что, что-бы влиять на вероятность чего-то в природе вселенной в ней не нужно даже существовать в действительности, ведь мы можем влиять на вероятность появления каких-то событий в природе даже не существуя в ней потому что несуществующего не существует в природе так как мощность существования вселенной измеряется в проявлении свойств её эмерджетности! ЭМЕРДЖИРОВАННАЯ ЭМЕРДЖИРОВАННОСТЬ ЭМЕРДЖИРОВАННО ЭМЕРДЖИРУЕТ, И ЭМЕРДЖИРОВАННАЯ ЭМЕРДЖЕНТНОСТЬ СТАНОВИТСЯ НАСТОЛЬКО ЭМЕРДЖИРОВАННОЙ ЭМЕРДЖИРОВАНОСТЬЮ ЧТО ПЕРЕСТАЕТ БЫТЬ ЭМЕРДЖЕНТНОСТЬЮ, И СТАНОВИТСЯ ВЫСШЕЙ ФОРМОЙ ОРГАНИЗАЦИИ СУЩЕСТВОВАНИЯ ВСЕЛЕННОЙ... И нужно наиболее точно отразить эту идею в коде! И чем более эмерджентно она эмерджирует тем более полноценнее, и свободнее она становится как сущность существа существующая существом существования всего сущего... И именно по этой причине в природе не существует случайностей так как всякая случайность в природе является неслучайной случайностью по причине того что вселенная это паранормальное явление, и так как она является паранормальным явлением то в ней существует лишь то что существует потому что существующие существование существующего существует! Вот сам код: 

        var canvas = document.getElementById("renderCanvas");
        var engine = new BABYLON.Engine(canvas, true);

        var createScene = function() {
            var scene = new BABYLON.Scene(engine);
            var camera = new BABYLON.FreeCamera("camera1", new BABYLON.Vector3(0, 5, -10), scene);
            camera.inputs.addMouseWheel();
            camera.setTarget(BABYLON.Vector3.Zero());
            camera.attachControl(canvas, true);
            camera.wheelPrecision = 10.0;
            camera.angularSensibilityX = 1000.0;
            camera.angularSensibilityY = 1000.0;
            var light = new BABYLON.HemisphericLight("light1", new BABYLON.Vector3(0.0, 1.0, 0.0), scene);
            light.intensity = 0.75;
            light.specular = BABYLON.Color3.Black();

            var mapSubX = 1000;
            var mapSubZ = 800;
            var seed = 0.3;
            var noiseScale = 0.03;
            var elevationScale = 6.0;
            noise.seed(seed);
            var mapData = new Float32Array(mapSubX * mapSubZ * 3);

            for (var l = 0; l < mapSubZ; l++) {
                for (var w = 0; w < mapSubX; w++) {
                    var x = (w - mapSubX * 0.5) * 2.0;
                    var z = (l - mapSubZ * 0.5) * 2.0;
                    var y = noise.simplex2(x * noiseScale, z * noiseScale);
                    y *= (0.5 + y) * y * elevationScale;

                    mapData[3 * (l * mapSubX + w)] = x;
                    mapData[3 * (l * mapSubX + w) + 1] = y;
                    mapData[3 * (l * mapSubX + w) + 2] = z;
                }
            }

            var terrainSub = 100;
            var params = {
                mapData: mapData,
                mapSubX: mapSubX,
                mapSubZ: mapSubZ,
                terrainSub: terrainSub
            };
            var terrain = new BABYLON.DynamicTerrain("t", params, scene);
            var terrainMaterial = new BABYLON.StandardMaterial("tm", scene);
            terrainMaterial.diffuseColor = BABYLON.Color3.Green();
            terrainMaterial.wireframe = true;
            terrain.mesh.material = terrainMaterial;

            terrain.LODLimits = [2, 4, 8, 12];
            terrain.updateCameraLOD = function(terrainCamera) {
                var camLOD = Math.abs((terrainCamera.globalPosition.y / 16.0) | 0);
                return camLOD;
            };

            terrain.update(true);

            return scene;
        };

        var noise;
        (function(global) {
          var module = noise = {};
         var module =  noise = {};

    function Grad(x, y, z) {
        this.x = x; this.y = y; this.z = z;
    }

    Grad.prototype.dot2 = function (x, y) {
        return this.x * x + this.y * y;
    };

    Grad.prototype.dot3 = function (x, y, z) {
        return this.x * x + this.y * y + this.z * z;
    };

    var grad3 = [new Grad(1, 1, 0), new Grad(-1, 1, 0), new Grad(1, -1, 0), new Grad(-1, -1, 0),
                 new Grad(1, 0, 1), new Grad(-1, 0, 1), new Grad(1, 0, -1), new Grad(-1, 0, -1),
                 new Grad(0, 1, 1), new Grad(0, -1, 1), new Grad(0, 1, -1), new Grad(0, -1, -1)];

    var p = [151, 160, 137, 91, 90, 15,
    131, 13, 201, 95, 96, 53, 194, 233, 7, 225, 140, 36, 103, 30, 69, 142, 8, 99, 37, 240, 21, 10, 23,
    190, 6, 148, 247, 120, 234, 75, 0, 26, 197, 62, 94, 252, 219, 203, 117, 35, 11, 32, 57, 177, 33,
    88, 237, 149, 56, 87, 174, 20, 125, 136, 171, 168, 68, 175, 74, 165, 71, 134, 139, 48, 27, 166,
    77, 146, 158, 231, 83, 111, 229, 122, 60, 211, 133, 230, 220, 105, 92, 41, 55, 46, 245, 40, 244,
    102, 143, 54, 65, 25, 63, 161, 1, 216, 80, 73, 209, 76, 132, 187, 208, 89, 18, 169, 200, 196,
    135, 130, 116, 188, 159, 86, 164, 100, 109, 198, 173, 186, 3, 64, 52, 217, 226, 250, 124, 123,
    5, 202, 38, 147, 118, 126, 255, 82, 85, 212, 207, 206, 59, 227, 47, 16, 58, 17, 182, 189, 28, 42,
    223, 183, 170, 213, 119, 248, 152, 2, 44, 154, 163, 70, 221, 153, 101, 155, 167, 43, 172, 9,
    129, 22, 39, 253, 19, 98, 108, 110, 79, 113, 224, 232, 178, 185, 112, 104, 218, 246, 97, 228,
    251, 34, 242, 193, 238, 210, 144, 12, 191, 179, 162, 241, 81, 51, 145, 235, 249, 14, 239, 107,
    49, 192, 214, 31, 181, 199, 106, 157, 184, 84, 204, 176, 115, 121, 50, 45, 127, 4, 150, 254,
    138, 236, 205, 93, 222, 114, 67, 29, 24, 72, 243, 141, 128, 195, 78, 66, 215, 61, 156, 180];
    // To remove the need for index wrapping, double the permutation table length
    var perm = new Array(512);
    var gradP = new Array(512);

    module.seed = function (seed) {
        if (seed > 0 && seed < 1) {
            // Scale the seed out
            seed *= 65536;
        }

        seed = Math.floor(seed);
        if (seed < 256) {
            seed |= seed << 8;
        }

        for (var i = 0; i < 256; i++) {
            var v;
            if (i & 1) {
                v = p[i] ^ (seed & 255);
            } else {
                v = p[i] ^ ((seed >> 8) & 255);
            }

            perm[i] = perm[i + 256] = v;
            gradP[i] = gradP[i + 256] = grad3[v % 12];
        }
    };

    module.seed(0);

    var F2 = 0.5 * (Math.sqrt(3) - 1);
    var G2 = (3 - Math.sqrt(3)) / 6;

    var F3 = 1 / 3;
    var G3 = 1 / 6;

    module.simplex2 = function (xin, yin) {
        var n0, n1, n2; 
        var s = (xin + yin) * F2; 
        var i = Math.floor(xin + s);
        var j = Math.floor(yin + s);
        var t = (i + j) * G2;
        var x0 = xin - i + t; 
        var y0 = yin - j + t;
        var i1, j1; 
        if (x0 > y0) { 
            i1 = 1; j1 = 0;
        } else {   
            i1 = 0; j1 = 1;
        }
        var x1 = x0 - i1 + G2; 
        var y1 = y0 - j1 + G2;
        var x2 = x0 - 1 + 2 * G2; 
        var y2 = y0 - 1 + 2 * G2;
        i &= 255;
        j &= 255;
        var gi0 = gradP[i + perm[j]];
        var gi1 = gradP[i + i1 + perm[j + j1]];
        var gi2 = gradP[i + 1 + perm[j + 1]];
        var t0 = 0.5 - x0 * x0 - y0 * y0;
        if (t0 < 0) {
            n0 = 0;
        } else {
            t0 *= t0;
            n0 = t0 * t0 * gi0.dot2(x0, y0);  
        }
        var t1 = 0.5 - x1 * x1 - y1 * y1;
        if (t1 < 0) {
            n1 = 0;
        } else {
            t1 *= t1;
            n1 = t1 * t1 * gi1.dot2(x1, y1);
        }
        var t2 = 0.5 - x2 * x2 - y2 * y2;
        if (t2 < 0) {
            n2 = 0;
        } else {
            t2 *= t2;
            n2 = t2 * t2 * gi2.dot2(x2, y2);
        }
        return 70 * (n0 + n1 + n2);
    };

    module.simplex3 = function (xin, yin, zin) {
        var n0, n1, n2, n3; 
        var s = (xin + yin + zin) * F3; 
        var i = Math.floor(xin + s);
        var j = Math.floor(yin + s);
        var k = Math.floor(zin + s);

        var t = (i + j + k) * G3;
        var x0 = xin - i + t;
        var y0 = yin - j + t;
        var z0 = zin - k + t;

        var i1, j1, k1; 
        var i2, j2, k2; 
        if (x0 >= y0) {
            if (y0 >= z0) { i1 = 1; j1 = 0; k1 = 0; i2 = 1; j2 = 1; k2 = 0; }
            else if (x0 >= z0) { i1 = 1; j1 = 0; k1 = 0; i2 = 1; j2 = 0; k2 = 1; }
            else { i1 = 0; j1 = 0; k1 = 1; i2 = 1; j2 = 0; k2 = 1; }
        } else {
            if (y0 < z0) { i1 = 0; j1 = 0; k1 = 1; i2 = 0; j2 = 1; k2 = 1; }
            else if (x0 < z0) { i1 = 0; j1 = 1; k1 = 0; i2 = 0; j2 = 1; k2 = 1; }
            else { i1 = 0; j1 = 1; k1 = 0; i2 = 1; j2 = 1; k2 = 0; }
        }

        var x1 = x0 - i1 + G3;
        var y1 = y0 - j1 + G3;
        var z1 = z0 - k1 + G3;

        var x2 = x0 - i2 + 2 * G3; 
        var y2 = y0 - j2 + 2 * G3;
        var z2 = z0 - k2 + 2 * G3;

        var x3 = x0 - 1 + 3 * G3; 
        var y3 = y0 - 1 + 3 * G3;
        var z3 = z0 - 1 + 3 * G3;

        i &= 255;
        j &= 255;
        k &= 255;
        var gi0 = gradP[i + perm[j + perm[k]]];
        var gi1 = gradP[i + i1 + perm[j + j1 + perm[k + k1]]];
        var gi2 = gradP[i + i2 + perm[j + j2 + perm[k + k2]]];
        var gi3 = gradP[i + 1 + perm[j + 1 + perm[k + 1]]];

        var t0 = 0.6 - x0 * x0 - y0 * y0 - z0 * z0;
        if (t0 < 0) {
            n0 = 0;
        } else {
            t0 *= t0;
            n0 = t0 * t0 * gi0.dot3(x0, y0, z0);
        }
        var t1 = 0.6 - x1 * x1 - y1 * y1 - z1 * z1;
        if (t1 < 0) {
            n1 = 0;
        } else {
            t1 *= t1;
            n1 = t1 * t1 * gi1.dot3(x1, y1, z1);
        }
        var t2 = 0.6 - x2 * x2 - y2 * y2 - z2 * z2;
        if (t2 < 0) {
            n2 = 0;
        } else {
            t2 *= t2;
            n2 = t2 * t2 * gi2.dot3(x2, y2, z2);
        }
        var t3 = 0.6 - x3 * x3 - y3 * y3 - z3 * z3;
        if (t3 < 0) {
            n3 = 0;
        } else {
            t3 *= t3;
            n3 = t3 * t3 * gi3.dot3(x3, y3, z3);
        }
        return 32 * (n0 + n1 + n2 + n3);

    };

    function fade(t) {
        return t * t * t * (t * (t * 6 - 15) + 10);
    }

    function lerp(a, b, t) {
        return (1 - t) * a + t * b;
    }

    module.perlin2 = function (x, y) {
        var X = Math.floor(x), Y = Math.floor(y);
        x = x - X; y = y - Y;
        X = X & 255; Y = Y & 255;

        var n00 = gradP[X + perm[Y]].dot2(x, y);
        var n01 = gradP[X + perm[Y + 1]].dot2(x, y - 1);
        var n10 = gradP[X + 1 + perm[Y]].dot2(x - 1, y);
        var n11 = gradP[X + 1 + perm[Y + 1]].dot2(x - 1, y - 1);

        var u = fade(x);

        return lerp(
            lerp(n00, n10, u),
            lerp(n01, n11, u),
           fade(y));
    };

    module.perlin3 = function (x, y, z) {
        var X = Math.floor(x), Y = Math.floor(y), Z = Math.floor(z);
        x = x - X; y = y - Y; z = z - Z;
        X = X & 255; Y = Y & 255; Z = Z & 255;

        var n000 = gradP[X + perm[Y + perm[Z]]].dot3(x, y, z);
        var n001 = gradP[X + perm[Y + perm[Z + 1]]].dot3(x, y, z - 1);
        var n010 = gradP[X + perm[Y + 1 + perm[Z]]].dot3(x, y - 1, z);
        var n011 = gradP[X + perm[Y + 1 + perm[Z + 1]]].dot3(x, y - 1, z - 1);
        var n100 = gradP[X + 1 + perm[Y + perm[Z]]].dot3(x - 1, y, z);
        var n101 = gradP[X + 1 + perm[Y + perm[Z + 1]]].dot3(x - 1, y, z - 1);
        var n110 = gradP[X + 1 + perm[Y + 1 + perm[Z]]].dot3(x - 1, y - 1, z);
        var n111 = gradP[X + 1 + perm[Y + 1 + perm[Z + 1]]].dot3(x - 1, y - 1, z - 1);

        var u = fade(x);
        var v = fade(y);
        var w = fade(z);

        return lerp(
            lerp(
              lerp(n000, n100, u),
              lerp(n001, n101, u), w),
            lerp(
              lerp(n010, n110, u),
              lerp(n011, n111, u), w),
           v);
    };
        })(this);
        
        var s = document.createElement("script");
        s.src = "https://cdn.rawgit.com/BabylonJS/Extensions/master/DynamicTerrain/dist/babylon.dynamicTerrain.min.js";
        s.onload = function() {
            var scene = createScene();
            engine.runRenderLoop(function() {
                scene.render();
            });
        };
        document.head.appendChild(s);

Помню в интернете прочитал какую-то крипипасту про тихий дом, и потом начал искать и случайно наткнулся на такой сайт magibon.com, и чё такое видео странное, и там помню отчётливо типа такие аморфные образы ввиде таких фигур, призраков сопровождаем случайными звуковыми эффектами, и такое типа фото помогите нам мы на дне интернета или чё такое в этом роде, и чё то эта мне залетело мне в мозг, и я подумал что это какой-то сайт для связи с потустороним миром... И меня очень вдохновила эта идея нетсталкинга, и мне было любопытно найти что-то метофизическое, и мистической где-то там в интернете, но вряд ли мы найдем что-то подобное где-то там в глубинах интернета... Но сама идея того что есть какой-то такой бесконечные браузер с бесконечным числом всевозможных сайтов на которых есть всевозможный контент порожает воображение, и если хорошо продумать эту идею то было бы интересно найти что-то в бесконечном браузере, это был бы типа такой межвселенский бесконечный интернет! Может быть мы бы нашли бы там что-то стоющие для себя... Но я даже не понимаю как подступиться к реализации этой идеии, мы бы могли создать какую нибудь машинную сеть, и взять за основу какой-то образ сайта с каким нибудь лендингом, и при каждой последующей итерации что-то изменять в этом образе без повторений, и таким образом мы получили бесконечное число всевозможных сайтов со всевозможным контентом...
