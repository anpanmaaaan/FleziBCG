import { Navigate } from "react-router";

import { useAuth } from "@/app/auth";
import { getDefaultLandingForPersona, resolvePersonaFromUser } from "./personaLanding.ts";

export function PersonaLandingRedirect() {
  const { currentUser } = useAuth();
  const persona = resolvePersonaFromUser(currentUser);

  return <Navigate to={getDefaultLandingForPersona(persona)} replace />;
}
