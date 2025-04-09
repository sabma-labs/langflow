// StarryBackground.tsx
import { useCallback } from "react";
import Particles from "react-tsparticles";
import { loadFull } from "tsparticles";

const StarryBackground = () => {
  const particlesInit = useCallback(async (engine) => {
    await loadFull(engine);
  }, []);

  return (
    <div className="fixed inset-0 -z-10">
      <Particles
        id="tsparticles"
        init={particlesInit}
        options={{
          fullScreen: { enable: false },
          background: {
            color: { value: "#000000" },
          },
          particles: {
            number: {
              value: 160,
              density: {
                enable: true,
                value_area: 800,
              },
            },
            color: { value: "#ffffff" },
            shape: { type: "circle" },
            opacity: {
              value: 0.4,
              random: true,
            },
            size: {
              value: 1.5,
              random: true,
            },
            move: {
              enable: true,
              speed: 0.2,
              direction: "none",
              outModes: { default: "out" },
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
    </div>
  );
};

export default StarryBackground;
