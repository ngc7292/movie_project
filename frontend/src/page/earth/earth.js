import './ThreeMap.css';
import React, { Component } from 'react';
import * as THREE from 'three';
import Stats from './common/threejslibs/stats.min.js';

class Earth extends Component{
    componentDidMount(){
        this.initEarth();
    }

    initEarth(){
        let container = document.getElementById("WebGL-output");
        let width = container.clientWidth;
        let height = container.clientHeight;
        let aspect = width / height;
        let renderer;
        let planet, scene, camera,group,stats;
        let asteroids;

        init();
        render();

        function init(){
            scene = new THREE.Scene();

            camera = new THREE.PerspectiveCamera(50 ,aspect, 0.1, 1000);
            camera.position.z = 500;

            group = new THREE.Group();
            group.add(new THREE.AmbientLight(0xFFFFFF, 0.2));

            let light = new THREE.DirectionalLight(0xFFFFFF, 3);
            light.position.set(1500, 2500, 0);
            scene.add(light);

            let material = new THREE.MeshLambertMaterial({ color: 0x0c2d4d});
            planet = new THREE.Mesh(
                new THREE.IcosahedronGeometry(100,3),
                // new THREE.TorusKnotGeometry(60,10,60,8,2,5),
                material
            );

            for(let i = 0;i<planet.geometry.vertices.length; i++)
                planet.geometry.vertices[i].multiplyScalar(
                    Math.random() * 0.05+1.0
                );
        
            planet.geometry.computeFlatVertexNormals();
            group.add(planet);

            asteroids = new THREE.Group();

            for (let p = 0; p < Math.PI * 2; p = p + Math.random() * 0.15) {
                let asteroid = new THREE.Mesh(
                    new THREE.IcosahedronGeometry(8, 0),
                    material
                );

                let size = Math.random() * 0.5;
                for (let i = 0; i < asteroid.geometry.vertices.length; i++)
                    asteroid.geometry.vertices[i].multiplyScalar(
                    Math.random() * 0.5 + size
                );

                let rand = Math.random() * 60 - 30;
                asteroid.position.set(200 * Math.sin(p) + rand, rand, 200 * Math.cos(p) + rand);

                asteroid.geometry.computeFlatVertexNormals();
                asteroids.add(asteroid);
            }
            group.add(asteroids);
            group.rotation.x = 0.1;
            group.rotation.y = -.3;
            group.rotation.z = -0.4;
        
            scene.add(group);

            for(let i=0;i<10;i++){
                let particles = new THREE.Points(
                    new THREE.Geometry(),
                    new THREE.PointsMaterial({
                        size: Math.random() * 5
                      })
                );
                for (let j = 0; j < 20; j++) {
                    var vertex = new THREE.Vector3();
                    vertex.x = Math.random() * width * 1.1 - width * 1.1 / 2;
                    vertex.y = Math.random() * height * 1.1 - height * 1.1 / 2;
                    vertex.z = -500;
                    particles.geometry.vertices.push(vertex);
                    particles.material.color.setScalar(Math.random() * 0.4 + 0.2);
                  }
                  scene.add(particles);
            }

            renderer = new THREE.WebGLRenderer();
            renderer.setSize(width, height);
            container.appendChild(renderer.domElement);
            stats = new Stats();
            container.appendChild( stats.dom );
        }

        function render() {
            requestAnimationFrame(render);

            planet.rotation.y += 0.001;
            planet.rotation.z -= 0.0005;
          
            asteroids.rotation.y += 0.003;
          
            renderer.render(scene, camera);

            stats.update();
        }
    }

    render(){
        return(
			<div id='WebGL-output' style={{ width:'80%', height: '600px' }}></div>
		)
    }
}

export default Earth;
