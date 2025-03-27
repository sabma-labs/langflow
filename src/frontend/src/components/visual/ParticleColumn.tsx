import { useEffect, useState } from "react";

const ParticleColumn = ({ side = "left" }: { side?: "left" | "right" }) => {
  const [particles, setParticles] = useState<Array<{ id: number; top: number }>>([]);

  useEffect(() => {
    const interval = setInterval(() => {
      setParticles((prev) => {
        const updated = prev.map((p) => ({ ...p, top: p.top - 1 }));
        return updated.filter((p) => p.top > -10).concat({
          id: Math.random(),
          top: 100 + Math.random() * 20,
        });
      });
    }, 100);
    return () => clearInterval(interval);
  }, []);

  return (
    <div
      className={`absolute ${side === "left" ? "left-4" : "right-4"} top-0 h-full w-1 z-10`}
    >
      {particles.map((p) => (
        <div
          key={p.id}
          className="w-[2px] h-[2px] bg-purple-400 rounded-full opacity-50 animate-fade"
          style={{ position: "absolute", top: `${p.top}%`, left: 0 }}
        />
      ))}
    </div>
  );
};

export default ParticleColumn;
