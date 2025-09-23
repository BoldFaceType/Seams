import * as fs from "fs";
export type Sig = { name: string; version: string; inputs: Record<string, any>; outputs: Record<string, any>; prompt_id: string; macro_id: string; agent_tool: string; };
export function loadSignature(p: string): Sig { return JSON.parse(fs.readFileSync(p, "utf-8")); }
