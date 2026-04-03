import { Navigate } from "react-router";

import { useAuth } from "../auth/AuthContext";
import { getDefaultLandingForPersona, resolvePersonaFromUser } from "./personaLanding.ts";

export function PersonaLandingRedirect() {
  const { currentUser } = useAuth();
  const persona = resolvePersonaFromUser(currentUser);

  return <Navigate to={getDefaultLandingForPersona(persona)} replace />;
}
