import nextTypescript from "eslint-config-next/typescript";
import nextCoreWebVitals from "eslint-config-next/core-web-vitals";

const eslintConfig = [...nextTypescript, // Global ignores
{
  ignores: ["node_modules", ".next", "out", "dist"],
}, ...nextCoreWebVitals];

export default eslintConfig;
