import GoogleLoginLogo from "@/assets/google-login.svg?react";
import AppleLoginLogo from "@/assets/apple-login.svg?react";
import Surreyxendlesslogo from "@/assets/SurreyxEndlesslogo.svg?react";
import { useLoginUser } from "@/controllers/API/queries/auth";
import { CustomLink } from "@/customization/components/custom-link";
import * as Form from "@radix-ui/react-form";
import { useContext, useState, useEffect } from "react";
import InputComponent from "../../components/core/parameterRenderComponent/components/inputComponent";
import { Button } from "../../components/ui/button";
import { Input } from "../../components/ui/input";
import { SIGNIN_ERROR_ALERT } from "../../constants/alerts_constants";
import { CONTROL_LOGIN_STATE } from "../../constants/constants";
import { AuthContext } from "../../contexts/authContext";
import useAlertStore from "../../stores/alertStore";
import { LoginType } from "../../types/api";
import {
  inputHandlerEventType,
  loginInputStateType,
} from "../../types/components";
import { IDE_VERSION } from "@/customization/feature-flags";
import MouseTrailMask from "@/components/common/effects/MouseTrailMask";
import { useNavigate } from "react-router-dom";
import SurreyxEndless from "@/assets/surreyxendless.svg?react";  // surreyxendless
import {
  connect,
  signMessage,
  UserResponseStatus,
} from "@endlesslab/endless-web3-sdk";

export default function LoginPage(): JSX.Element {
  const [inputState, setInputState] =
    useState<loginInputStateType>(CONTROL_LOGIN_STATE);

  const { password, username } = inputState;
  const { login } = useContext(AuthContext);
  const setErrorData = useAlertStore((state) => state.setErrorData);

  function handleInput({
    target: { name, value },
  }: inputHandlerEventType): void {
    setInputState((prev) => ({ ...prev, [name]: value }));
  }

  const { mutate } = useLoginUser();

  const handleWalletLogin = async () => {
    try {
      // Step 1: 请求钱包连接授权
      const walletConnection = await connect();
      if (walletConnection.status !== UserResponseStatus.APPROVED) {
        throw new Error("User rejected wallet connection");
      }

      const accountAddress = walletConnection.args.address;

      // Step 2: 构造签名信息并请求签名
      const message = "Login to Endless App";
      const signatureResult = await signMessage({ message });

      if (signatureResult.status !== UserResponseStatus.APPROVED) {
        throw new Error("User rejected signature");
      }

      const { signature, fullMessage, publicKey } = signatureResult.args;

      // Step 3: 调用后端进行登录验证（假设你有这个接口）
      const res = await fetch("/api/auth/wallet-login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          address: accountAddress,
          message,
          signature,
          fullMessage,
          publicKey,
        }),
      });

      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Wallet login failed");

      // Step 4: 保存 token 并跳转
      login(data.access_token, "wallet", data.refresh_token);
      navigate("/flows");

    } catch (err: any) {
      console.error("Wallet login error:", err);
      setErrorData({
        title: "Wallet Login Error",
        list: [err.message || "Unexpected error"],
      });
    }
  };
  const [mousePos, setMousePos] = useState({ x: 0, y: 0 });
  const navigate = useNavigate();
  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      setMousePos({ x: e.clientX, y: e.clientY });
    };

    window.addEventListener("mousemove", handleMouseMove);
    return () => window.removeEventListener("mousemove", handleMouseMove);
  }, []);
  const handleGoogleLogin = async () => {
    console.log("Google Sign In clicked");
    // 你可以在这里接入 Google OAuth 或跳转
  };
  const handleAppleLogin = () => {
    console.log("Apple Sign In clicked");
    // 你可以在这里接入 Apple OAuth 或跳转
  };
  //console.log("点击登录按钮, username:", username, "password:", password);
  function signIn() {
    const user: LoginType = {
      username: username.trim(),
      password: password.trim(),
    };

    mutate(user, {
      onSuccess: (data) => {
        console.log("登录成功:", data);
        login(data.access_token, "login", data.refresh_token);
        navigate("/flows");
      },
      onError: (error) => {
        console.error("登录失败:", error);
        setErrorData({
          title: SIGNIN_ERROR_ALERT,
          list: [error["response"]["data"]["detail"]],
        });
      },
    });
  }

  return (

    <Form.Root
      onSubmit={(event) => {
        if (password === "") {
          event.preventDefault();
          return;
        }
        signIn();
        const data = Object.fromEntries(new FormData(event.currentTarget));
        event.preventDefault();
      }}
      className="h-screen w-full"
    >
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

        <div className="absolute top-6 left-6 z-20 flex items-center space-x-2">
  <SurreyxEndless className="h-8 w-auto opacity-90" />
  <span className="text-white font-mono text-2xl leading-none pt-[0px]">lab</span>
</div>
      <div className="relative z-10 flex h-full w-full flex-col items-center justify-center">
        <div className="flex w-84 flex-col items-center justify-center gap-2">
          <Surreyxendlesslogo
            title="Surrey-endless logo"
            className="mb-4 h-20 w-30 scale-[1]"
          />
          <span className="mb-6 font-semibold text-2xl text-primary">
            Link to the Endless Wallet
          </span>
          <div className="mb-3 w-full">
            <Form.Field name="username">
              <Form.Label className="data-[invalid]:label-invalid">
                Username <span className="font-medium text-destructive">*</span>
              </Form.Label>

              <Form.Control asChild>
                <Input
                  type="username"
                  onChange={({ target: { value } }) => {
                    handleInput({ target: { name: "username", value } });
                  }}
                  value={username}
                  className="w-full"
                  required
                  placeholder="Username"
                />
              </Form.Control>

              <Form.Message match="valueMissing" className="field-invalid">
                Please enter your username
              </Form.Message>
            </Form.Field>
          </div>
          <div className="mb-3 w-full">
            <Form.Field name="password">
              <Form.Label className="data-[invalid]:label-invalid">
                Password <span className="font-medium text-destructive">*</span>
              </Form.Label>

              <InputComponent
                onChange={(value) => {
                  handleInput({ target: { name: "password", value } });
                }}
                value={password}
                isForm
                password={true}
                required
                placeholder="Password"
                className="w-full"
              />

              <Form.Message className="field-invalid" match="valueMissing">
                Please enter your password
              </Form.Message>
            </Form.Field>
          </div>
          <div className="w-full">
            <Form.Submit asChild>
              <Button className="mr-3 mt-6 w-full" type="submit">
                Sign in
              </Button>
            </Form.Submit>
            <div className="w-full">
            <CustomLink to="/signup">
              <Button className="w-full" variant="outline" type="button">
                Don't have an account?&nbsp;<b>Sign Up</b>
              </Button>
            </CustomLink>
          </div>
            {/* Google 登录按钮 */}
            <div className="w-full mt-4">
              <div className="rounded-xl bg-white/5 p-4 border border-white/10 shadow-lg backdrop-blur-md">
                <h3 className="text-sm text-white font-semibold mb-2">
                  Or sign in using:
                </h3>
                <button
                  type="button"
                  onClick={handleGoogleLogin}
                  className="flex items-center gap-3 w-full px-4 py-2 rounded-md border border-gray-300 bg-white hover:bg-gray-100 transition-all"
                >
                  <span className="w-12 flex justify-center">
                    <GoogleLoginLogo className="w-5 h-5" />
                  </span>
                  <span className="text-sm font-medium text-gray-700 leading-none">
                    Google Sign In Wallet
                  </span>
                </button>

              <button
              type="button"
              onClick={handleAppleLogin}
              className="mt-3 flex items-center gap-3 w-full px-4 py-2 rounded-md border border-gray-300 bg-white hover:bg-gray-100 transition-all"
            >
              <span className="w-12 flex justify-center">
                <AppleLoginLogo className="w-5 h-5" />
              </span>
              <span className="text-sm font-medium text-gray-700 leading-none">
                Apple Sign In Wallet
              </span>
            </button>
            <Button
            type="button"
            onClick={handleWalletLogin}
            variant="secondary"
            className="mt-3 w-full"
          >
            Sign in with Wallet
          </Button>
              </div>
            </div>
          </div>

        </div>
      </div>
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
    </Form.Root>
  );
}
