var canvas = document.getElementById("renderCanvas");
var engine = new BABYLON.Engine(canvas, true);

var createScene = function() {
    var scene = new BABYLON.Scene(engine);
    var camera = new BABYLON.ArcRotateCamera("camera", 0, 0, 10, BABYLON.Vector3.Zero(), scene);
    camera.attachControl(canvas, true);
    camera.wheelPrecision = 100;
    camera.lowerRadiusLimit = 5;
    camera.upperRadiusLimit = 20;

    var light = new BABYLON.HemisphericLight("light", new BABYLON.Vector3(1, 1, 0), scene);
    light.intensity = 0.7;

    var foamGradientMaterial = new BABYLON.StandardMaterial("foamGradient", scene);
    foamGradientMaterial.diffuseColor = new BABYLON.Color3(1, 1, 1);
    foamGradientMaterial.alpha = 0.5;

    var foamMeshes = [];
    var numFoamMeshes = Math.floor(Math.random() * 30) + 1;

    for (var i = 0; i < numFoamMeshes; i++) {
        var foamMesh = BABYLON.MeshBuilder.CreateBox("foamBox" + i, { size: 1 }, scene);
        foamMesh.material = foamGradientMaterial;
        foamMesh.position = new BABYLON.Vector3(
            Math.random() * 20 - 10, 
            Math.random() * 20 - 10, 
            Math.random() * 20 - 10
        );
        foamMesh.scaling = new BABYLON.Vector3(
            Math.random() * 5 + 1, 
            Math.random() * 5 + 1, 
            Math.random() * 5 + 1
        );
        foamMesh.rotation = new BABYLON.Vector3(
            Math.random() * Math.PI * 2, 
            Math.random() * Math.PI * 2, 
            Math.random() * Math.PI * 2
        );
        foamMeshes.push(foamMesh);
    }

    scene.registerBeforeRender(function() {
        for (var i = 0; i < foamMeshes.length; i++) {
            var foamMesh = foamMeshes[i];
            var time = performance.now() * 0.001;

            foamMesh.position.x += Math.cos(time * 0.5) * 0.1;
            foamMesh.position.y += Math.sin(time * 0.3) * 0.1;
            foamMesh.position.z += Math.sin(time * 0.7) * 0.1;

            foamMesh.rotation.y += 0.01;
            foamMesh.rotation.z += 0.01;

            foamMesh.scaling.x += (Math.random() - 0.5) * 0.01;
            foamMesh.scaling.y += (Math.random() - 0.5) * 0.01;
            foamMesh.scaling.z += (Math.random() - 0.5) * 0.01;

            foamMesh.visibility = Math.random() > 0.5 ? 1.0 : 0.0;
        }
    });

    return scene;
};

var scene = createScene();

engine.runRenderLoop(function() {
    scene.render();
});
