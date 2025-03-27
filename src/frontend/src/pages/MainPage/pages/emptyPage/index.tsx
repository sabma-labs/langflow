import { useEffect, useState } from "react";
import LangflowLogo from "@/assets/endlesslogo.svg?react";
import Endlesstext from "@/assets/endlesstext.svg?react";
import Surreyxendlesslogo from "@/assets/SurreyxEndlesslogo.svg?react";
import ForwardedIconComponent from "@/components/common/genericIconComponent";
import CardsWrapComponent from "@/components/core/cardsWrapComponent";
import { Button } from "@/components/ui/button";
import { useFolderStore } from "@/stores/foldersStore";
import useFileDrop from "../../hooks/use-on-file-drop";
import MouseTrailMask from "@/components/common/effects/MouseTrailMask";
//import EdgeGlowLine from "@/components/visual/EdgeGlowLine";
//import ParticleColumn from "@/components/visual/ParticleColumn";
//import CodeRain from "@/components/visual/CodeRain";
import { IDE_VERSION } from "@/customization/feature-flags";

type EmptyPageProps = {
  setOpenModal: (open: boolean) => void;
};

export const EmptyPage = ({ setOpenModal }: EmptyPageProps) => {
  const folders = useFolderStore((state) => state.folders);
  const handleFileDrop = useFileDrop(undefined);
  const [mousePos, setMousePos] = useState({ x: 0, y: 0 });

  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      setMousePos({ x: e.clientX, y: e.clientY });
    };

    window.addEventListener("mousemove", handleMouseMove);
    return () => window.removeEventListener("mousemove", handleMouseMove);
  }, []);

  return (
    <CardsWrapComponent
      dragMessage={`Drop your flows or components here`}
      onFileDrop={handleFileDrop}
    >
      <div className="m-0 h-full w-full bg-black relative overflow-hidden">
        {/* 背景图层 + 点阵 + 模糊遮罩 */}


        <svg
          width="100%"
          height="100%"
          style={{ position: "absolute", top: 0, left: 0, zIndex: 1 }}
        >
          <defs>
            {/* 点阵图案 */}

            <pattern
              id="bdotPattern"
              patternUnits="userSpaceOnUse"
              width="15"
              height="15"
            >
              <circle cx="3" cy="3" r="1" fill="white" />
            </pattern>

            {/* 模糊光圈渐变 */}
            <radialGradient id="softCircle" cx="50%" cy="40%" r="60%">
              <stop offset="0%" stopColor="black" stopOpacity="0.95" />
              <stop offset="60%" stopColor="black" stopOpacity="0.8" />
              <stop offset="100%" stopColor="black" stopOpacity="0.96" />
            </radialGradient>

            {/* 蒙版 */}
            <mask id="mouseMask">
              <rect width="100%" height="100%" fill="white" />
              // circle 的中心为鼠标位置
              <MouseTrailMask />
            </mask>
            </defs>

            {/* 背景图案 */}
            <rect width="100%" height="100%" fill="url(#bdotPattern)" />
            {/* 模糊光圈 */}

            <rect
              width="100%"
              height="100%"
              fill="url(#softCircle)"
              mask="url(#mouseMask)"
            />

        </svg>
        {/* <CodeRain side="left" />
        <CodeRain side="right" /> */}

        {/*<ParticleColumn side="left" />
        <ParticleColumn side="right" />
         <EdgeGlowLine position="left" />
        <EdgeGlowLine position="right" /> */}


        <div className="absolute left-6 bottom-10 z-10 text-white opacity-40 font-mono text-m leading-tight select-none">
        <div>{`[ █ ▒ ▓ ░ ]`}</div>
        <div className="mt-1">{`< protocol ${IDE_VERSION} >`}</div>
        <div className="mt-1">{`[∞ endless]`}</div>
        </div>

        <div className="absolute right-6 bottom-10 z-10 text-white opacity-40 font-mono text-m leading-tight text-right select-none">
        <div>{`< status: ready >`}</div>
        <div className="mt-1">{`:: 0x003D...F`}</div>
        <div className="mt-1">{`{ Cloud · DApp · Edge }`}</div>
        </div>

        {/* 居中文本层 */}
        <div
          className="absolute inset-0 z-10 flex flex-col items-center justify-center text-center px-4"
        >
          <Surreyxendlesslogo className="h-16 w-50 mb-4" />
          <h3
            className="pt-2 text-2xl font-semibold text-white flex items-center gap-2"
            data-testid="mainpage_title"
            >
            {folders?.length > 1 ? (
                "Empty folder"
            ) : (
                <>
                {/* <Endlesstext className="h-6 w-auto" /> */}
                <span className="font-mono text-primary">Surrey x Endless Lab</span>
                </>
            )}
            </h3>
            {/* 添加垂直空间 */}
            <div className="h-5"></div>
          <p
            data-testid="empty-folder-description"
            className="pb-5 text-m text-neutral-400"
          >
            Begin with a template, or start from scratch.
          </p>
          <div className="h-3"></div>
          <Button
            variant="default"
            onClick={() => setOpenModal(true)}
            id="new-project-btn"
            data-testid="new_project_btn_empty_page"
          >
            <ForwardedIconComponent
              name="Plus"
              aria-hidden="true"
              className="h-4 w-4"
            />
            <span className="hidden whitespace-nowrap font-semibold md:inline">
              BUILD  YOUR  DAPP
            </span>
          </Button>
        </div>

        {/* 导航和社交链接按钮组 */}
        <div className="absolute bottom-4 left-0 right-0 z-10 flex flex-col items-center justify-center gap-2 text-lg text-white pointer-events-auto">

          {/* 图标行 */}
        <div className="flex gap-6 mt-1">
            <a href="https://github.com/endless-labs/" target="_blank" rel="noopener noreferrer" className="hover:opacity-100 opacity-60 transition-opacity">
            <img src="../../../../src/icons/social/Githublogo.svg" alt="GitHub" className="w-8 h-8" />
            </a>
            <a href="https://x.com/EndlessProtocol" target="_blank" rel="noopener noreferrer" className="hover:opacity-100 opacity-60 transition-opacity">
            <img src="../../../../src/icons/social/Xlogo.svg" alt="X" className="w-8 h-8" />
            </a>
            <a href="https://www.luffa.im/" target="_blank" rel="noopener noreferrer" className="hover:opacity-100 opacity-60 transition-opacity">
            <img src="../../../../src/icons/social/Luffalogo.svg" alt="Luffa" className="w-8 h-8" />
            </a>
        </div>
        <div className="h-1"></div>
        {/* 顶部链接行 */}
        <div className="flex gap-5">
            <a href="https://www.surrey.ac.uk/academy-for-blockchain-and-metaverse-applications" target="_blank" rel="noopener noreferrer" className="hover:underline opacity-70 hover:opacity-100">
            SABMA in Surrey
            </a>
            <a href="https://endless.link/" target="_blank" rel="noopener noreferrer" className="hover:underline opacity-70 hover:opacity-100">
            Endless Home
            </a>
            <a href="https://docs.endless.link/endless/discovery/discovery-endless-protocol" target="_blank" rel="noopener noreferrer" className="hover:underline opacity-70 hover:opacity-100">
            Endless Docs
            </a>
        </div>


        {/* 添加制作单位 SABMA 小字 */}
        <div className="mt-1 text-xs opacity-60">Surrey Academy for Blockchain and Metaverse Applications, University of Surrey</div>
        </div>
      </div>
    </CardsWrapComponent>
  );
};

export default EmptyPage;
