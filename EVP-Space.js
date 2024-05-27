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

    // Создаем кубическую сетку
    var gridSize = 2; // размер сетки 2x2 метра
    var gridSubdivisions = 100; // количество подразделений сетки
    var grid = new BABYLON.GridMaterial("grid", scene);
    grid.gridRatio = gridSize;
    grid.majorUnitFrequency = 0;
    grid.minorUnitVisibility = 0;
    grid.opacity = 0; // сетка невидима
    grid.backFaceCulling = false;

    // Создаем кубы с случайными цветами и прозрачностью
    for (var x = -gridSize * gridSubdivisions / 2; x < gridSize * gridSubdivisions / 2; x += gridSize) {
        for (var z = -gridSize * gridSubdivisions / 2; z < gridSize * gridSubdivisions / 2; z += gridSize) {
            var box = BABYLON.MeshBuilder.CreateBox("box", {size: gridSize}, scene);
            box.position.x = x;
            box.position.z = z;
            box.material = new BABYLON.StandardMaterial("boxMat", scene);
            box.material.diffuseColor = new BABYLON.Color4(Math.random(), Math.random(), Math.random(), Math.random());
            box.material.alpha = Math.random(); // случайная прозрачность
        }
    }

    return scene;
};

var scene = createScene();
engine.runRenderLoop(function() {
    scene.render();
});

// Добавляем управление камерой
scene.onBeforeRenderObservable.add(() => {
    if (scene.activeCamera) {
        scene.activeCamera.attachControl(canvas);
    }
});
