import { useEffect, useRef, useState } from "react";

import { useAuthStore } from "@/store/auth";

type Options = {
  enabled?: boolean;
  onMessage?: (data: unknown) => void;
  onError?: (err: unknown) => void;
};

export const useWebSocket = (path: string, opts: Options = {}) => {
  const { enabled = true, onMessage, onError } = opts;
  const [readyState, setReadyState] = useState<number>(0);
  const wsRef = useRef<WebSocket | null>(null);
  const token = useAuthStore((s) => s.token);

  useEffect(() => {
    if (!enabled) return;
    const proto = window.location.protocol === "https:" ? "wss:" : "ws:";
    const url = `${proto}//${window.location.host}${path}${token ? `?token=${token}` : ""}`;
    const ws = new WebSocket(url);
    wsRef.current = ws;

    ws.onopen = () => setReadyState(ws.readyState);
    ws.onclose = () => setReadyState(ws.readyState);
    ws.onerror = (e) => {
      onError?.(e);
      setReadyState(ws.readyState);
    };
    ws.onmessage = (event) => {
      try {
        onMessage?.(JSON.parse(event.data));
      } catch {
        onMessage?.(event.data);
      }
    };

    return () => ws.close();
  }, [enabled, path, token]); // eslint-disable-line react-hooks/exhaustive-deps

  return { readyState, send: (data: unknown) => wsRef.current?.send(typeof data === "string" ? data : JSON.stringify(data)) };
};
