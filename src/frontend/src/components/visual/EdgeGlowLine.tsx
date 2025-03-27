const EdgeGlowLine = ({ position = "left" }: { position?: "left" | "right" }) => {
    const isLeft = position === "left";

    return (
      <div className={`absolute top-0 bottom-0 ${isLeft ? "left-0" : "right-0"} z-10 pointer-events-none`}>
        {/* 背后 glow 模糊层 */}
        <div
          className={`w-[6px] h-full ${isLeft ? "bg-gradient-to-r" : "bg-gradient-to-l"}
            from-purple-500/30 via-purple-400/20 to-transparent
            blur-md opacity-70`}
        />

        {/* 细线边界 */}
        <div
          className={`absolute top-0 ${isLeft ? "left-0" : "right-0"} w-[2px] h-full
            bg-purple-500 animate-pulse`}
        />
      </div>
    );
  };

  export default EdgeGlowLine;
