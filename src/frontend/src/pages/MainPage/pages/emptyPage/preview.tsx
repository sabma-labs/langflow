import { useEffect, useRef, useState } from "react";
import LangflowLogo from "@/assets/endlesslogo.svg?react";
import ForwardedIconComponent from "@/components/common/genericIconComponent";
import CardsWrapComponent from "@/components/core/cardsWrapComponent";
import { Button } from "@/components/ui/button";
import { useFolderStore } from "@/stores/foldersStore";
import useFileDrop from "../../hooks/use-on-file-drop";

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
        {/* 点阵背景 + 蒙版 */}
        <svg
          width="100%"
          height="100%"
          style={{ position: "absolute", top: 0, left: 0, zIndex: 1 }}
        >
          <defs>
            <pattern
              id="dotPattern"
              patternUnits="userSpaceOnUse"
              width="20"
              height="20"
            >
              <circle cx="10" cy="10" r="2" fill="white" />
            </pattern>

            <mask id="mouseMask">
              <rect width="100%" height="100%" fill="white" />
              <circle
                cx={mousePos.x}
                cy={mousePos.y}
                r="60"
                fill="black"
              />
            </mask>
          </defs>

          <rect width="100%" height="100%" fill="url(#dotPattern)" />
          <rect
            width="100%"
            height="100%"
            fill="black"
            mask="url(#mouseMask)"
          />
        </svg>

        {/* 正文内容 */}
        <div
          className="relative z-20 flex w-full flex-col items-center justify-center gap-2"
          style={{ position: "relative", zIndex: 2 }}
        >
          <LangflowLogo className="h-14 w-16" />
          <h3
            className="pt-5 font-chivo text-2xl font-semibold text-white"
            data-testid="mainpage_title"
          >
            {folders?.length > 1 ? "Empty folder" : "ENDLESS IDE"}
          </h3>
          <p
            data-testid="empty-folder-description"
            className="pb-5 text-sm text-neutral-400"
          >
            Begin with a Endless template, or start from scratch.
          </p>
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
              START BUILDING YOUR ENDLESS APP
            </span>
          </Button>
        </div>
      </div>
    </CardsWrapComponent>
  );
};

export default EmptyPage;
