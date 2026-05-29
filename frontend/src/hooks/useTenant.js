import { useEffect, useState } from "react";

const TENANT_KEY = "esg.tenant";

export function getStoredTenant() {
  return localStorage.getItem(TENANT_KEY) || "demo-org";
}

export default function useTenant() {
  const [tenant, setTenantState] = useState(getStoredTenant());

  useEffect(() => {
    const handle = () => setTenantState(getStoredTenant());
    window.addEventListener("tenant-updated", handle);
    return () => window.removeEventListener("tenant-updated", handle);
  }, []);

  const setTenant = (value) => {
    const next = String(value || "").trim();
    if (!next) return;
    localStorage.setItem(TENANT_KEY, next);
    setTenantState(next);
    window.dispatchEvent(new CustomEvent("tenant-updated"));
  };

  return { tenant, setTenant };
}
