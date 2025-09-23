import * as vscode from "vscode";
import { loadSignature, Sig } from "./signature-loader";
import { runAgentTool } from "./rpc-agent";
import * as fs from "fs";
import * as path from "path";

async function getPromptList(context: vscode.ExtensionContext): Promise<{name:string; desc:string; sigPath:string}[]> {
  try {
    const res = await fetch("http://127.0.0.1:8765/prompts.json");
    if (res.ok) {
      const items = await res.json() as any[];
      return items.map(it => ({ name: it.name, desc: it.description ?? "", sigPath: "" }));
    }
  } catch {}
  const dir = path.join(context.extensionPath, "signatures");
  if (!fs.existsSync(dir)) return [];
  const entries = fs.readdirSync(dir).filter(f => f.endsWith(".json"));
  return entries.map(f => {
    const p = path.join(dir, f);
    const sig = loadSignature(p);
    return { name: sig.name, desc: sig.prompt_id ?? "", sigPath: p };
  });
}

export function activate(context: vscode.ExtensionContext) {
  const runCmd = vscode.commands.registerCommand("macro.run", async () => {
    try {
      const sigPath = path.join(context.extensionPath, "signatures", "refactor_python_function.json");
      const sig: Sig = loadSignature(sigPath);
      const editor = vscode.window.activeTextEditor;
      const code = editor?.document.getText() ?? "";
      if (!code) { vscode.window.showWarningMessage("Open a Python file with content to refactor."); return; }
      const goal = await vscode.window.showQuickPick(["optimize","clarify","type-annotate"], { placeHolder: "Goal" }); if (!goal) return;
      const constraintsRaw = await vscode.window.showInputBox({ prompt: "Constraints (comma-separated)", value: "pep8" });
      const seedRaw = await vscode.window.showInputBox({ prompt: "Seed (optional integer)", value: "" });
      const constraints = (constraintsRaw ?? "").split(",").map(s => s.trim()).filter(Boolean);
      const seed = seedRaw && seedRaw.trim() ? Number(seedRaw) : undefined;
      const payload: any = { code, goal, constraints }; if (seed !== undefined && !Number.isNaN(seed)) payload.seed = seed;
      const result = await runAgentTool(sig.agent_tool, payload);
      const doc = await vscode.workspace.openTextDocument({ content: result.code, language: "python" });
      await vscode.window.showTextDocument(doc, { preview: true });
      vscode.window.showInformationMessage(`Notes: ${result.notes}`);
    } catch (err:any) { vscode.window.showErrorMessage(`Seams macro error: ${err?.message || err}`); }
  });

  const menuCmd = vscode.commands.registerCommand("macro.menu", async () => {
    const items = await getPromptList(context);
    if (!items.length) { vscode.window.showInformationMessage("No prompts found."); return; }
    const pick = await vscode.window.showQuickPick(items.map(i => ({ label: i.name, detail: i.desc, sigPath: i.sigPath })), { placeHolder: "Choose a prompt" });
    if (!pick) return;
    if (pick.sigPath) {
      const sig: Sig = loadSignature(pick.sigPath);
      const editor = vscode.window.activeTextEditor;
      const code = editor?.document.getText() ?? "";
      if (!code) { vscode.window.showWarningMessage("Open a Python file to supply 'code' input."); return; }
      const goal = await vscode.window.showQuickPick(["optimize","clarify","type-annotate"], { placeHolder: "Goal" }); if (!goal) return;
      const constraintsRaw = await vscode.window.showInputBox({ prompt: "Constraints (comma-separated)", value: "pep8" });
      const seedRaw = await vscode.window.showInputBox({ prompt: "Seed (optional integer)", value: "" });
      const constraints = (constraintsRaw ?? "").split(",").map(s => s.trim()).filter(Boolean);
      const seed = seedRaw && seedRaw.trim() ? Number(seedRaw) : undefined;
      const payload: any = { code, goal, constraints }; if (seed !== undefined && !Number.isNaN(seed)) payload.seed = seed;
      const result = await runAgentTool(sig.agent_tool, payload);
      const doc = await vscode.workspace.openTextDocument({ content: result.code, language: "python" });
      await vscode.window.showTextDocument(doc, { preview: true });
      vscode.window.showInformationMessage(`Notes: ${result.notes}`);
    } else {
      await vscode.env.clipboard.writeText(`python seams.py run --name ${pick.label} --json '{...}'`);
      vscode.window.showInformationMessage("Copied CLI run command to clipboard.");
    }
  });

  const graphMenu = vscode.commands.registerCommand("macro.graphMenu", async () => {
    try {
      const res = await fetch("http://127.0.0.1:8765/graphs.json");
      if (!res.ok) { vscode.window.showWarningMessage("No graphs endpoint. Start server."); return; }
      const items = await res.json() as any[];
      if (!items.length) { vscode.window.showInformationMessage("No graphs registered."); return; }
      const pick = await vscode.window.showQuickPick(items.map(i => ({ label: i.name })), { placeHolder: "Choose a graph" });
      if (!pick) return;
      const chosen = items.find(i => i.name === pick.label);
      const props = (chosen?.input?.properties ?? {});
      const example: any = {}; for (const k of Object.keys(props)) { const t = props[k].type; example[k] = (t==="integer") ? 0 : (t==="array" ? [] : ""); }
      const payloadStr = await vscode.window.showInputBox({ prompt: "Graph input JSON", value: JSON.stringify(example) });
      if (!payloadStr) return;
      const url = `http://127.0.0.1:8765/graph/${encodeURIComponent(pick.label)}`;
      const r = await fetch(url, { method: "POST", headers: { "Content-Type": "application/json" }, body: payloadStr });
      if (!r.ok) { vscode.window.showErrorMessage(`Graph run failed: ${r.status}`); return; }
      const out = await r.json();
      const doc = await vscode.workspace.openTextDocument({ content: JSON.stringify(out, null, 2), language: "json" });
      await vscode.window.showTextDocument(doc, { preview: true });
    } catch (e:any) { vscode.window.showErrorMessage(`Graph Menu error: ${e?.message || e}`); }
  });

  context.subscriptions.push(runCmd, menuCmd, graphMenu);
}

export function deactivate() {}
