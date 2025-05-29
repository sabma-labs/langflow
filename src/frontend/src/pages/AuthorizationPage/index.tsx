import { useEffect, useState, useContext } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import * as Form from "@radix-ui/react-form";
import { Button } from "../../components/ui/button";
import InputComponent from "../../components/core/parameterRenderComponent/components/inputComponent";
import Surreyxendlesslogo from "@/assets/SurreyxEndlesslogo.svg?react";
import StarryBackground from "@/components/visual/StarryBackground";
import useAlertStore from "../../stores/alertStore";
import { AuthContext } from "../../contexts/authContext";
import { connectAndSubmit } from "./walletService";

interface RequestData {
  id: string;
  data: Record<string, any>;
  target_user_id: string;
}

export default function AuthorizationPage(): JSX.Element {
  const { accessToken } = useContext(AuthContext);
  const [searchParams] = useSearchParams();
  const requestId = searchParams.get("id");
  const [request, setRequest] = useState<RequestData | null>(null);
  const [fields, setFields] = useState<Record<string, any>>({});
  const [loading, setLoading] = useState(true);
  const [showButton, setShowButton] = useState(false);
  const [authorizing, setAuthorizing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);
  const setErrorData = useAlertStore((state) => state.setErrorData);
  const navigate = useNavigate();

  useEffect(() => {
    if (!requestId) {
      setErrorData({ title: "Missing ID", list: ["No request ID provided in URL"] });
      setLoading(false);
      return;
    }

    async function fetchRequest() {
        try {
          const api = process.env.BACKEND_URL
          const res = await fetch(
            `${api}/api/v1/user_input/?id=${requestId}`,
            {
              method: 'GET',
              headers: {
                "ngrok-skip-browser-warning": "true",
                "accept": "application/json"
              },
            }
          );
          if (!res.ok) {
            const err = await res.json();
            throw new Error(err.detail || "Failed to load request data");
          }
          const json: RequestData = await res.json();
          const parsed = typeof json.data === 'string' ? JSON.parse(json.data) : json.data;
          setRequest(json);
          setFields(parsed);
          setShowButton(true);
        } catch (err: unknown) {
          const message = err instanceof Error ? err.message : "Unexpected load error";
          setErrorData({ title: "Load Error", list: [message] });
          if (message.includes("Not authorized")) {
            navigate("/unauthorized");
          }
        } finally {
          setLoading(false);
        }
      }

    fetchRequest();
  }, [requestId, accessToken, setErrorData, navigate]);

  const handleAuthorize = async () => {
    setError(null);
    setSuccess(false);
    setAuthorizing(true);
    try {
            // connect, sign & submit
            await connectAndSubmit(fields);
            
            // let the user know, then close
            alert("Transaction completed successfully");
            window.close();
            
            // in case window.close() is blocked by the browser, still set success
             setSuccess(true);
            
          } catch (err: unknown) {
             const message = err instanceof Error ? err.message : "Authorization failed";
             setError(message);
           } finally {
             setAuthorizing(false);
           }
  };

  if (loading) {
    return <div className="h-screen flex items-center justify-center">Loading...</div>;
  }

  return (
    <div className="h-screen w-full relative">
      <StarryBackground className="absolute inset-0 z-0" />
      <svg width="100%" height="100%" className="absolute top-0 left-0 z-10">
        {/* … pattern & mask definitions … */}
      </svg>
      <div className="relative z-20 flex h-full w-full items-center justify-center">
        <div className="flex w-84 flex-col items-center gap-4 p-6 bg-white/5 border border-white/10 rounded-xl shadow-lg backdrop-blur-md">
          <Surreyxendlesslogo className="h-20 w-auto mb-2" title="Surrey-Endless" />
          <span className="text-2xl font-semibold text-primary mb-4">Authorize Request</span>
          <Form.Root className="w-full space-y-4">
            {Object.entries(fields).map(([key, value]) => (
              <Form.Field key={key} name={key}>
                <Form.Label className="capitalize">
                  {key
                    .split('_')
                    .map(w => w.charAt(0).toUpperCase() + w.slice(1))
                    .join(' ')}
                </Form.Label>
                <Form.Control asChild>
                  <InputComponent value={String(value)} readOnly />
                </Form.Control>
              </Form.Field>
            ))}
            {showButton && (
              <Button
                type="button"
                onClick={handleAuthorize}
                disabled={authorizing}
                className="w-full mt-4"
              >
                {authorizing ? 'Authorizing…' : 'Authorize'}
              </Button>
            )}
            {success && <div className="text-green-500 text-center">Authorization successful</div>}
            {error && <div className="text-red-500 text-center">{error}</div>}
          </Form.Root>
        </div>
      </div>
    </div>
  );
}
