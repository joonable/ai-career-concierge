"use client";

import Link from "next/link";
import { useEffect, useRef } from "react";

import * as THREE from "three";

type WovenLightHeroProps = {
  headlineClassName: string;
  bodyClassName: string;
};

const HEADLINE = "AI Career Concierge";
const SUBCOPY = "정말 검토할 가치가 있는 공고만 남깁니다.";

export function WovenLightHero({
  headlineClassName,
  bodyClassName,
}: WovenLightHeroProps) {
  const words = HEADLINE.split(" ");

  return (
    <section className="woven-hero">
      <WovenCanvas />
      <div className="woven-hero__veil" />

      <nav className="woven-nav">
        <div className="woven-nav__brand">
          <span className="woven-nav__mark" aria-hidden="true">
            ⎎
          </span>
          <span className={bodyClassName}>AI Career Concierge</span>
        </div>
      </nav>

      <div className="woven-hero__content">
        <h1 className={`woven-hero__headline ${headlineClassName}`}>
          {words.map((word, wordIndex) => (
            <span className="woven-hero__word" key={word}>
              {word.split("").map((char, charIndex) => (
                <span key={`${word}-${charIndex}`} className="woven-hero__char">
                  {char}
                </span>
              ))}
              {wordIndex < words.length - 1 ? <span>&nbsp;</span> : null}
            </span>
          ))}
        </h1>

        <p className={`woven-hero__subcopy ${bodyClassName}`}>
          {SUBCOPY}
        </p>

        <div className="woven-hero__cta-wrap">
          <Link className={`woven-hero__cta ${bodyClassName}`} href="/login">
            로그인
          </Link>
        </div>
      </div>
    </section>
  );
}

function WovenCanvas() {
  const mountRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const mountNode = mountRef.current;
    if (!mountNode) {
      return;
    }

    const particleCount = window.innerWidth < 768 ? 6000 : 12000;
    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(56, window.innerWidth / window.innerHeight, 0.1, 1000);
    camera.position.z = 5.2;

    const renderer = new THREE.WebGLRenderer({
      antialias: true,
      alpha: true,
      powerPreference: "high-performance",
    });
    renderer.setSize(window.innerWidth, window.innerHeight);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 1.8));
    mountNode.appendChild(renderer.domElement);

    const geometry = new THREE.BufferGeometry();
    const sourceGeometry = new THREE.TorusKnotGeometry(1.55, 0.42, 220, 28);
    const sourcePositions = sourceGeometry.attributes.position;

    const positions = new Float32Array(particleCount * 3);
    const originalPositions = new Float32Array(particleCount * 3);
    const velocities = new Float32Array(particleCount * 3);
    const colors = new Float32Array(particleCount * 3);

    for (let index = 0; index < particleCount; index += 1) {
      const vertexIndex = index % sourcePositions.count;
      const ix = index * 3;
      const x = sourcePositions.getX(vertexIndex);
      const y = sourcePositions.getY(vertexIndex);
      const z = sourcePositions.getZ(vertexIndex);

      positions[ix] = x;
      positions[ix + 1] = y;
      positions[ix + 2] = z;
      originalPositions[ix] = x;
      originalPositions[ix + 1] = y;
      originalPositions[ix + 2] = z;

      const hue = 0.55 + Math.random() * 0.16;
      const color = new THREE.Color().setHSL(hue, 0.78, 0.62 + Math.random() * 0.12);
      colors[ix] = color.r;
      colors[ix + 1] = color.g;
      colors[ix + 2] = color.b;
    }

    geometry.setAttribute("position", new THREE.BufferAttribute(positions, 3));
    geometry.setAttribute("color", new THREE.BufferAttribute(colors, 3));

    const material = new THREE.PointsMaterial({
      size: 0.016,
      vertexColors: true,
      transparent: true,
      opacity: 0.92,
      blending: THREE.AdditiveBlending,
      depthWrite: false,
    });

    const points = new THREE.Points(geometry, material);
    points.rotation.x = -0.35;
    scene.add(points);

    const clock = new THREE.Clock();
    let pointerX = 0;
    let pointerY = 0;
    let animationFrameId = 0;

    const handlePointerMove = (event: PointerEvent) => {
      pointerX = (event.clientX / window.innerWidth) * 2 - 1;
      pointerY = -((event.clientY / window.innerHeight) * 2 - 1);
    };

    const handleResize = () => {
      camera.aspect = window.innerWidth / window.innerHeight;
      camera.updateProjectionMatrix();
      renderer.setSize(window.innerWidth, window.innerHeight);
      renderer.setPixelRatio(Math.min(window.devicePixelRatio, 1.8));
    };

    const animate = () => {
      animationFrameId = window.requestAnimationFrame(animate);

      const elapsedTime = clock.getElapsedTime();
      const mouseWorldX = pointerX * 3.1;
      const mouseWorldY = pointerY * 2.2;

      for (let index = 0; index < particleCount; index += 1) {
        const ix = index * 3;
        const currentX = positions[ix];
        const currentY = positions[ix + 1];
        const currentZ = positions[ix + 2];
        const originX = originalPositions[ix];
        const originY = originalPositions[ix + 1];
        const originZ = originalPositions[ix + 2];

        let velocityX = velocities[ix];
        let velocityY = velocities[ix + 1];
        let velocityZ = velocities[ix + 2];

        const dx = currentX - mouseWorldX;
        const dy = currentY - mouseWorldY;
        const distanceSq = dx * dx + dy * dy;

        if (distanceSq > 0.0001 && distanceSq < 2.25) {
          const distance = Math.sqrt(distanceSq);
          const force = (1.5 - distance) * 0.012;
          const inverseDistance = 1 / distance;
          velocityX += dx * inverseDistance * force;
          velocityY += dy * inverseDistance * force;
        }

        velocityX += (originX - currentX) * 0.0018;
        velocityY += (originY - currentY) * 0.0018;
        velocityZ += (originZ - currentZ) * 0.0014;

        velocityX *= 0.94;
        velocityY *= 0.94;
        velocityZ *= 0.94;

        positions[ix] = currentX + velocityX;
        positions[ix + 1] = currentY + velocityY;
        positions[ix + 2] = currentZ + velocityZ;

        velocities[ix] = velocityX;
        velocities[ix + 1] = velocityY;
        velocities[ix + 2] = velocityZ;
      }

      geometry.attributes.position.needsUpdate = true;
      points.rotation.y = elapsedTime * 0.06;
      points.rotation.z = Math.sin(elapsedTime * 0.2) * 0.08;

      renderer.render(scene, camera);
    };

    window.addEventListener("pointermove", handlePointerMove, { passive: true });
    window.addEventListener("resize", handleResize);
    animate();

    return () => {
      window.cancelAnimationFrame(animationFrameId);
      window.removeEventListener("pointermove", handlePointerMove);
      window.removeEventListener("resize", handleResize);

      scene.remove(points);
      sourceGeometry.dispose();
      geometry.dispose();
      material.dispose();
      renderer.dispose();

      if (mountNode.contains(renderer.domElement)) {
        mountNode.removeChild(renderer.domElement);
      }
    };
  }, []);

  return <div ref={mountRef} className="woven-canvas" aria-hidden="true" />;
}
