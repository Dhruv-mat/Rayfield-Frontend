import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { LoginPage } from "./screens/LoginPage";

createRoot(document.getElementById("app") as HTMLElement).render(
  <StrictMode>
    <LoginPage />
  </StrictMode>,
);
