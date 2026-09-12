export const getApiBase = (): string => {
  if (process.env.NEXT_PUBLIC_API_URL) {
    return process.env.NEXT_PUBLIC_API_URL;
  }
  
  if (typeof window !== "undefined") {
    const host = window.location.hostname;
    const devtunnelMatch = host.match(/^([a-zA-Z0-9]+)-(\d+)\.(.*devtunnels\.ms)$/);
    if (devtunnelMatch) {
      const [_, tunnelId, port, rest] = devtunnelMatch;
      return `https://${tunnelId}-8008.${rest}`;
    }
  }

  return "http://localhost:8008";
};

export const getWsBase = (): string => {
  const apiBase = getApiBase();
  if (apiBase.startsWith("https://")) {
    return apiBase.replace("https://", "wss://");
  }
  return apiBase.replace("http://", "ws://");
};

export const API_BASE = getApiBase();
export const WS_BASE = getWsBase();
