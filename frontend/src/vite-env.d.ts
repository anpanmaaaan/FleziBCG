/// <reference types="vite/client" />

interface ImportMetaEnv {
	readonly VITE_PERSONA_ENFORCEMENT_MODE?: "DEV" | "STRICT";
}

interface ImportMeta {
	readonly env: ImportMetaEnv;
}

declare module '*.png';
declare module '*.jpg';
declare module '*.jpeg';
declare module '*.svg';
declare module '*.gif';
declare module '*.webp';
