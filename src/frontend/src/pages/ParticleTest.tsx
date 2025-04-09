import { useCallback } from "react";
import Particles from "react-tsparticles";
import { loadFull } from "tsparticles";

const ParticleTest = () => {
  const particlesInit = useCallback(async (engine) => {
    await loadFull(engine);
  }, []);

  return (
    <div className="relative w-screen h-screen overflow-hidden bg-black">
      <Particles
        id="tsparticles"
        init={particlesInit}
        className="absolute inset-0 z-0"
        options={{
          background: {
            color: {
              value: "#000000",
            },
          },
          fpsLimit: 60,
          particles: {
            number: {
              value: 100,
              density: {
                enable: true,
                value_area: 800,
              },
            },
            color: {
              value: "#ffffff",
            },
            shape: {
              type: "circle",
            },
            opacity: {
              value: 0.5,
            },
            size: {
              value: 2,
            },
            move: {
              enable: true,
              speed: 0.5,
              direction: "none",
              outModes: {
                default: "bounce",
              },
            },
            links: {
              enable: false,
            },
          },
          interactivity: {
            events: {
              onHover: {
                enable: true,
                mode: "repulse",
              },
              resize: true,
            },
            modes: {
              repulse: {
                distance: 100,
                duration: 0.4,
              },
            },
          },
          detectRetina: true,
        }}
      />
      <div className="relative z-10 flex items-center justify-center h-full text-white text-3xl">
        粒子背景测试
      </div>
    </div>
  );
};

export default ParticleTest;
